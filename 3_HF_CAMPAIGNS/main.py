"""
=============================================================================
HEALTHFINDER - CAMPAÑA DE EMAIL MARKETING GALICIA
Enfoque: Digital (Posicionamiento Google) + Pedidos Directos
=============================================================================

Estrategia de envío:
1. Priorizar por reputación (baja reputación + web = candidatos ideales)
2. ~50 emails/día (no levantar sospechas de proveedores)
3. Desde email de empresa: angel.martinez@novaquality.es
4. Logs y tracking para follow-up manual (antes de "llamadas frías")

Productos:
- DIGITAL: Posicionamiento en Google (para farmacias sin presencia)
- PEDIDOS_DIRECTOS: Sistema de recomendación de pedidos

"""

import pandas as pd
import smtplib
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import json
import os
from dotenv import load_dotenv

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

load_dotenv()

CONFIG = {
    'SENDER_EMAIL': os.getenv('SMTP_USER', 'angel.martinez@novaquality.es'),
    'SENDER_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
    'SMTP_SERVER': os.getenv('SMTP_HOST', 'smtp.office365.com'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
    
    # Rate limiting
    'EMAILS_PER_DAY': int(os.getenv('RATE_LIMIT_EMAILS_PER_DAY', 50)),
    'MIN_DELAY_SECONDS': 20,
    'MAX_DELAY_SECONDS': 45,
    
    # Campaign info
    'CAMPAIGN_NAME': 'HF_GALICIA_2025_Q1',
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Healthfinder'),
    'SENDER_NAME': os.getenv('SENDER_NAME', 'Ángel Martínez'),
    'SENDER_POSITION': os.getenv('SENDER_POSITION', 'Consultor de Digitalización Farmacéutica'),
    'DRY_RUN': os.getenv('DRY_RUN', 'True').lower() == 'true',
}

# Rutas
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f'campaign_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CLASES
# ============================================================================

class FarmaciaAnalyzer:
    """Análisis y priorización de farmacias."""
    
    PRIORIDADES = {
        'tier_1': {'score': 100, 'name': 'CRÍTICA', 'description': 'Mala reputación + web (MÁS NECESITAN DIGITAL)'},
        'tier_2': {'score': 75, 'name': 'ALTA', 'description': 'Baja reputación + web'},
        'tier_3': {'score': 50, 'name': 'MEDIA', 'description': 'Reputación OK + web'},
        'tier_4': {'score': 25, 'name': 'BAJA', 'description': 'Sin web (pedidos directos prioritario)'},
    }
    
    @staticmethod
    def calculate_priority_score(farmacia: Dict) -> Dict:
        """
        Calcula score de prioridad basado en:
        - Rating (0-5): Cuanto menor, más lo necesita
        - Num reseñas: Indicador de visibilidad
        - Tiene web: Factor crítico para digital
        - Edad del edificio: Proxy de "tradición vs modernidad"
        """
        
        rating = float(farmacia.get('rating', 5.0)) or 5.0
        reviews = float(farmacia.get('reviews', 0)) or 0
        has_web = str(farmacia.get('site', '')).strip().lower() not in ('', 'null', 'none', 'nan')
        has_email = str(farmacia.get('email', '')).strip().lower() not in ('', 'null', 'none', 'nan')
        
        # Base: cuanto menor el rating, más urgente
        rating_score = (5 - rating) * 20  # 0-100
        
        # Reseñas: menos reseñas = menos visibilidad
        reviews_score = min(50, reviews * 2)  # Cap 50
        reviews_penalty = max(0, 50 - reviews_score)  # Penaliza pocas reseñas
        
        # Web es CRÍTICO para campaña digital
        web_factor = 30 if has_web else -50
        
        # Email es importante para contacto
        email_factor = 10 if has_email else 0
        
        total_score = rating_score + reviews_penalty + web_factor + email_factor
        total_score = max(0, min(100, total_score))  # Clamp 0-100
        
        # Asignar tier
        if has_web and rating < 4.0 and reviews < 30:
            tier = 'tier_1'
        elif has_web and rating < 4.5:
            tier = 'tier_2'
        elif has_web:
            tier = 'tier_3'
        else:
            tier = 'tier_4'
        
        return {
            'score': total_score,
            'tier': tier,
            'tier_name': FarmaciaAnalyzer.PRIORIDADES[tier]['name'],
            'rating_score': rating_score,
            'reviews_score': reviews_score,
            'has_web': has_web,
            'has_email': has_email,
        }
    
    @staticmethod
    def categorize_product(farmacia: Dict) -> List[str]:
        """
        Determina qué productos ofrecer a cada farmacia basado en su perfil.
        
        DIGITAL: Si tiene web (para mejorar posicionamiento)
        PEDIDOS_DIRECTOS: Siempre (todos necesitan optimizar stock)
        """
        products = []
        
        has_web = str(farmacia.get('site', '')).strip().lower() not in ('', 'null', 'none', 'nan')
        
        if has_web:
            products.append('DIGITAL')
        
        products.append('PEDIDOS_DIRECTOS')  # Para todos
        
        return products


class EmailTemplateGenerator:
    """Genera emails personalizados según producto."""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
    
    def generate_digital_email(self, farmacia: Dict) -> tuple[str, str]:
        """Email para Digital - Posicionamiento en Google."""
        
        nombre = farmacia.get('name', 'Farmacéutico').split()[0]  # Primer nombre
        provincia = farmacia.get('provincia', 'Galicia')
        municipio = farmacia.get('municipio', '')
        
        subject = f"📍 Posiciona '{nombre}' en Google - Recibe más clientes"
        
        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
            
            <div style="max-width: 600px; margin: 0 auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">📍 Posicionamiento en Google</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px;">Más clientes = Más ventas</p>
                </div>
                
                <!-- Contenido -->
                <div style="padding: 30px 20px;">
                    
                    <p><strong>Hola {nombre},</strong></p>
                    
                    <p>
                        En <strong>{provincia}</strong> hay +1,300 farmacias. ¿Y tú? 
                        <strong>¿Apareces en las primeras 3 posiciones cuando un cliente busca "farmacia en {municipio}"?</strong>
                    </p>
                    
                    <div style="background: #f0f4ff; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0;"><strong>El 82% de clientes buscan farmacias en Google antes de visitarlas</strong></p>
                        <p style="margin: 5px 0 0 0; font-size: 13px; color: #555;">Si no apareces, pierdes clientes.</p>
                    </div>
                    
                    <h3 style="color: #667eea; margin-top: 25px;">Nuestro Servicio Digital:</h3>
                    <ul style="line-height: 1.8;">
                        <li>✅ <strong>Auditoría</strong> de tu presencia en Google (sin coste)</li>
                        <li>✅ <strong>Optimización</strong> de tu perfil de Google Business</li>
                        <li>✅ <strong>Gestión</strong> de reseñas y reputación online</li>
                        <li>✅ <strong>Publicidad</strong> local en Google Maps (si deseas)</li>
                    </ul>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; text-align: center;">
                        <p style="margin: 0; font-weight: bold; color: #d39e00;">
                            📞 Primeras 20 farmacias: Auditoría GRATIS
                        </p>
                        <p style="margin: 8px 0 0 0; font-size: 12px; color: #666;">Desde HOY hasta el 15 de Febrero</p>
                    </div>
                    
                    <p>
                        Si quieres que tu farmacia sea la que aparece primero cuando alguien busca en Google:
                    </p>
                    
                    <!-- CTA -->
                    <div style="text-align: center; margin: 25px 0;">
                        <a href="https://healthfinder.es/auditar?farmacia={farmacia.get('name', '')}&provincia={provincia}" 
                           style="display: inline-block; background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 15px; transition: background-color 0.3s;">
                            🚀 SOLICITAR AUDITORÍA GRATIS
                        </a>
                    </div>
                    
                    <p style="font-size: 13px; color: #666; margin-top: 20px; text-align: center;">
                        O responde directamente a este email si tienes dudas.
                    </p>
                    
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                    <p style="margin: 0; text-align: center;">
                        <strong>Healthfinder</strong> | Soluciones Digitales para Farmacias
                    </p>
                    <p style="margin: 5px 0 0 0; text-align: center;">
                        📧 {CONFIG['COMPANY_EMAIL']} | 🌐 {CONFIG['COMPANY_WEB']}
                    </p>
                    <p style="margin: 10px 0 0 0; text-align: center; font-size: 11px; color: #999;">
                        No deseamos recibir más emails: <a href="https://healthfinder.es/unsubscribe" style="color: #999;">Darse de baja</a>
                    </p>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        return subject, html
    
    def generate_pedidos_email(self, farmacia: Dict) -> tuple[str, str]:
        """Email para Pedidos Directos - Sistema de recomendación de pedidos."""
        
        nombre = farmacia.get('name', 'Farmacéutico').split()[0]
        
        subject = f"📦 Pedidos Inteligentes - Reduce stock muerto {nombre}"
        
        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
            
            <div style="max-width: 600px; margin: 0 auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">📦 Pedidos Inteligentes</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px;">Menos errores, más margen</p>
                </div>
                
                <!-- Contenido -->
                <div style="padding: 30px 20px;">
                    
                    <p><strong>Hola {nombre},</strong></p>
                    
                    <p>
                        ¿Cuántas veces al mes dices: <strong>"Debería haber pedido más de esto"</strong> o 
                        <strong>"¿Para qué pedí esto si no se vende?"</strong>
                    </p>
                    
                    <div style="background: #ffe0e6; border-left: 4px solid #f5576c; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0;">Stock muerto = dinero atrapado. Stockout = clientes perdidos.</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px; color: #555;"><strong>Existe un término medio.</strong></p>
                    </div>
                    
                    <h3 style="color: #f5576c; margin-top: 25px;">Cómo funciona:</h3>
                    <ul style="line-height: 1.9;">
                        <li><strong>1️⃣ Indicador</strong>: Estableces días de cobertura (ej: 7 días) y cantidad mínima</li>
                        <li><strong>2️⃣ Sistema recomendador</strong>: Te mostramos qué CN pedir y cuántas unidades</li>
                        <li><strong>3️⃣ Un click</strong>: Envías la orden a tu distribuidor favorito</li>
                        <li><strong>4️⃣ Resultados</strong>: -15% rotación, +5% margen neto (casos reales)</li>
                    </ul>
                    
                    <h4 style="color: #f5576c; margin-top: 20px;">Casos de éxito:</h4>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 4px; font-size: 13px;">
                        📊 <strong>Farmacia Centro</strong>: "Reduje ruptura de stock en cosmética un 40%"<br>
                        📊 <strong>Farmacia Periférica</strong>: "Identifiqué 3 productos "cementerio" - ¡venderé!"
                    </div>
                    
                    <p style="margin-top: 20px;">
                        Y todo DESDE TU EMAIL - No necesitas instalaciones complicadas, sin cambios en tu ERP Farmatic.
                    </p>
                    
                    <!-- CTA -->
                    <div style="text-align: center; margin: 25px 0;">
                        <a href="https://healthfinder.es/pedidos?farmacia={farmacia.get('name', '')}" 
                           style="display: inline-block; background-color: #f5576c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 15px; transition: background-color 0.3s;">
                            🎯 VER DEMOSTRACIÓN
                        </a>
                    </div>
                    
                    <p style="font-size: 13px; color: #666; margin-top: 20px;">
                        📞 <strong>Responde a este email</strong> si quieres una demostración personalizada<br>
                        ⏱️ Toma 15 minutos y podemos usar <strong>TUS datos</strong> reales.
                    </p>
                    
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                    <p style="margin: 0; text-align: center;">
                        <strong>Healthfinder</strong> | Soluciones Digitales para Farmacias
                    </p>
                    <p style="margin: 5px 0 0 0; text-align: center;">
                        📧 {CONFIG['COMPANY_EMAIL']} | 🌐 {CONFIG['COMPANY_WEB']}
                    </p>
                    <p style="margin: 10px 0 0 0; text-align: center; font-size: 11px; color: #999;">
                        Menos contactos: <a href="https://healthfinder.es/unsubscribe" style="color: #999;">Darse de baja</a>
                    </p>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        return subject, html


class EmailCampaignOrchestrator:
    """Orquesta la campaña completa de emails."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.analyzer = FarmaciaAnalyzer()
        self.generator = EmailTemplateGenerator(TEMPLATES_DIR)
        self.sent_today = 0
        self.session = None
        
    def load_data(self) -> pd.DataFrame:
        """Carga datos de farmacias desde CSV."""
        try:
            df = pd.read_csv(DATA_DIR / 'farmacias_galicia.csv')
            logger.info(f"✅ Cargadas {len(df)} farmacias")
            return df
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            return pd.DataFrame()
    
    def prioritize_farmacias(self, df: pd.DataFrame, tier_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Añade columnas de prioridad y filtra por tier si es necesario.
        
        Devuelve: DataFrame ordenado por prioridad
        """
        # Calcular scores
        df['priority_data'] = df.apply(self.analyzer.calculate_priority_score, axis=1)
        
        # Expandir columnas
        df['priority_score'] = df['priority_data'].apply(lambda x: x['score'])
        df['priority_tier'] = df['priority_data'].apply(lambda x: x['tier'])
        df['tier_name'] = df['priority_data'].apply(lambda x: x['tier_name'])
        df['has_web'] = df['priority_data'].apply(lambda x: x['has_web'])
        df['has_email'] = df['priority_data'].apply(lambda x: x['has_email'])
        
        # Filtrar si es necesario
        if tier_filter:
            df = df[df['priority_tier'] == tier_filter].copy()
        
        # Ordenar por prioridad (desc) + por reseñas (asc para baja reputación)
        df = df.sort_values(
            by=['priority_score', 'reviews'],
            ascending=[False, True]
        ).reset_index(drop=True)
        
        logger.info(f"\n{'DISTRIBUCIÓN POR TIER':=^60}")
        for tier in ['tier_1', 'tier_2', 'tier_3', 'tier_4']:
            count = len(df[df['priority_tier'] == tier])
            if count > 0:
                tier_name = self.analyzer.PRIORIDADES[tier]['name']
                desc = self.analyzer.PRIORIDADES[tier]['description']
                logger.info(f"  {tier_name:20} | {count:4} farmacias | {desc}")
        
        return df
    
    def prepare_campaign_batch(self, df: pd.DataFrame, batch_size: int = 50) -> List[Dict]:
        """
        Prepara lotes de emails para envío.
        Cada farmacia puede recibir 1 o 2 emails (según productos).
        """
        campaigns = []
        
        for idx, row in df.iterrows():
            farmacia = row.to_dict()
            
            # Validar email
            email = str(farmacia.get('email', '')).strip()
            if not email or email.lower() in ('null', 'none', 'nan', ''):
                continue
            
            # Categorizar productos a ofrecer
            products = self.analyzer.categorize_product(farmacia)
            
            # Crear una entrada por producto
            for product in products:
                if product == 'DIGITAL':
                    subject, html = self.generator.generate_digital_email(farmacia)
                else:  # PEDIDOS_DIRECTOS
                    subject, html = self.generator.generate_pedidos_email(farmacia)
                
                campaigns.append({
                    'email': email,
                    'name': farmacia.get('name', 'Farmacia'),
                    'municipio': farmacia.get('municipio', ''),
                    'provincia': farmacia.get('provincia', ''),
                    'priority_tier': farmacia.get('priority_tier', ''),
                    'priority_score': farmacia.get('priority_score', 0),
                    'product': product,
                    'subject': subject,
                    'html': html,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending'
                })
        
        logger.info(f"\n{'CAMPAÑA PREPARADA':=^60}")
        logger.info(f"  Total de emails a enviar: {len(campaigns)}")
        logger.info(f"  Distribuidos en {(len(campaigns) // self.config['EMAILS_PER_DAY']) + 1} días")
        
        return campaigns
    
    def send_email(self, to_email: str, subject: str, html: str) -> bool:
        """Envía un email individual."""
        try:
            if not self.session:
                self.session = smtplib.SMTP(self.config['SMTP_SERVER'], self.config['SMTP_PORT'])
                self.session.starttls()
                self.session.login(self.config['SENDER_EMAIL'], self.config['SENDER_PASSWORD'])
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config['SENDER_EMAIL']
            msg['To'] = to_email
            
            part = MIMEText(html, 'html', 'utf-8')
            msg.attach(part)
            
            self.session.send_message(msg)
            logger.info(f"✅ Email enviado a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando a {to_email}: {e}")
            self._reconnect_smtp()
            return False
    
    def _reconnect_smtp(self):
        """Reconecta la sesión SMTP tras error."""
        try:
            if self.session:
                self.session.quit()
        except:
            pass
        self.session = None
    
    def log_campaign_send(self, campaign: Dict, status: str = 'sent'):
        """Registra el envío en el log de tracking."""
        tracking_file = LOGS_DIR / f"campaign_tracking_{datetime.now().strftime('%Y%m%d')}.csv"
        
        log_entry = pd.DataFrame([{
            'timestamp': datetime.now().isoformat(),
            'email': campaign['email'],
            'nombre_farmacia': campaign['name'],
            'municipio': campaign['municipio'],
            'provincia': campaign['provincia'],
            'product': campaign['product'],
            'priority_tier': campaign['priority_tier'],
            'status': status,
            'subject': campaign['subject'][:50]
        }])
        
        if tracking_file.exists():
            df_existing = pd.read_csv(tracking_file)
            df_combined = pd.concat([df_existing, log_entry], ignore_index=True)
            df_combined.to_csv(tracking_file, index=False, encoding='utf-8')
        else:
            log_entry.to_csv(tracking_file, index=False, encoding='utf-8')
    
    def launch_daily_batch(self, campaigns: List[Dict], day_number: int = 1):
        """
        Lanza un lote diario de ~50 emails.
        
        Args:
            campaigns: Lista de emails a enviar (puede ser parcial)
            day_number: Número de día (para logging)
        """
        batch_size = self.config['EMAILS_PER_DAY']
        batch = campaigns[:batch_size]
        
        logger.info(f"\n{'DÍA ' + str(day_number) + ' - LANZANDO BATCH':=^60}")
        logger.info(f"  {len(batch)} emails a enviar")
        logger.info(f"  Duración aproximada: {len(batch) * 30 / 60:.1f} minutos")
        
        sent_count = 0
        failed_count = 0
        
        for i, campaign in enumerate(batch):
            # Rate limiting
            delay = random.uniform(
                self.config['MIN_DELAY_SECONDS'],
                self.config['MAX_DELAY_SECONDS']
            )
            time.sleep(delay)
            
            # Enviar
            success = self.send_email(
                campaign['email'],
                campaign['subject'],
                campaign['html']
            )
            
            if success:
                self.log_campaign_send(campaign, status='sent')
                sent_count += 1
            else:
                self.log_campaign_send(campaign, status='failed')
                failed_count += 1
            
            # Progress
            if (i + 1) % 10 == 0:
                logger.info(f"  [{i+1}/{len(batch)}] - Enviados: {sent_count}, Fallos: {failed_count}")
        
        logger.info(f"\n  ✅ Enviados: {sent_count}")
        logger.info(f"  ❌ Fallos: {failed_count}")
        
        return batch


# ============================================================================
# EJECUCIÓN
# ============================================================================

def main():
    """Script principal."""
    
    logger.info("="*70)
    logger.info(f"HEALTHFINDER - CAMPAÑA GALICIA {CONFIG['CAMPAIGN_NAME']}")
    logger.info("="*70)
    
    # 1. Instanciar orquestador
    orchestrator = EmailCampaignOrchestrator(CONFIG)
    
    # 2. Cargar datos
    df_farmacias = orchestrator.load_data()
    if df_farmacias.empty:
        logger.error("No hay datos para procesar. Abortando.")
        return
    
    # 3. Priorizar (comenzar con Tier 1)
    df_prioritized = orchestrator.prioritize_farmacias(df_farmacias, tier_filter='tier_1')
    
    if df_prioritized.empty:
        logger.warning("No hay farmacias en Tier 1. Expandiendo a Tier 2...")
        df_prioritized = orchestrator.prioritize_farmacias(df_farmacias, tier_filter='tier_2')
    
    # 4. Preparar campaña
    campaigns = orchestrator.prepare_campaign_batch(df_prioritized)
    
    if not campaigns:
        logger.error("No se pudieron preparar emails. Abortando.")
        return
    
    # 5. Simular modo DRY-RUN (descomenta para envío real)
    logger.info("\n" + "="*70)
    logger.info("🔍 MODO DRY-RUN: Mostrando primeros 5 emails (SIN ENVIAR)")
    logger.info("="*70)
    
    for i, campaign in enumerate(campaigns[:5]):
        logger.info(f"\n[{i+1}] {campaign['email']} | {campaign['product']}")
        logger.info(f"    Asunto: {campaign['subject']}")
        logger.info(f"    Tier: {campaign['priority_tier']} (Score: {campaign['priority_score']:.0f})")
    
    logger.info("\n" + "="*70)
    logger.info("💡 Para enviar de verdad, descomenta la línea de envío en main.py")
    logger.info("="*70)
    
    # ENVÍO REAL (descomenta para activar):
    # response = input("\n¿Enviar batch? (s/n): ").lower()
    # if response == 's':
    #     orchestrator.launch_daily_batch(campaigns, day_number=1)


if __name__ == '__main__':
    main()
