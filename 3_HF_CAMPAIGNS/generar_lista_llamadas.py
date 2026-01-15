"""
=============================================================================
GENERADOR DE LISTA PRIORIZADA DE LLAMADAS
Healthfinder - Seguimiento Post-Email
=============================================================================

Analiza el tracking de emails enviados y genera una lista Excel priorizada
de farmacias para llamar por teléfono.

Criterios de priorización:
1. Tier (40%): Tier 1 > Tier 2 > Tier 3 > Tier 4
2. Email Status (30%): Abierto sin clic > No abierto > Bounced
3. Tiempo (20%): 3-5 días óptimo, >14 días descartado
4. Teléfono (10%): Debe tener teléfono disponible

"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DATA_DIR = Path('data')
TRACKING_FILE = DATA_DIR / 'tracking' / 'emails_sent.csv'
FARMACIAS_FILE = DATA_DIR / 'farmacias_galicia.csv'
OUTPUT_FILE = Path('output') / 'lista_llamadas_priorizada.xlsx'

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuración de priorización
TIER_WEIGHTS = {
    'tier_1': 100,
    'tier_2': 70,
    'tier_3': 40,
    'tier_4': 10
}

STATUS_WEIGHTS = {
    'opened_no_click': 100,
    'not_opened': 50,
    'clicked_no_demo': 100,  # Muy alto: mostró interés
    'bounced': 30
}

TIEMPO_OPTIMO_DIAS = (3, 5)  # Ventana óptima

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def limpiar_telefono(phone):
    """Limpia y valida números de teléfono."""
    if pd.isna(phone) or phone == '':
        return None
    
    phone_str = str(phone).strip()
    # Eliminar espacios, guiones, paréntesis
    phone_clean = phone_str.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Validar longitud (España: 9 dígitos sin prefijo, o 11-12 con prefijo)
    if len(phone_clean) >= 9:
        return phone_clean
    return None

def calcular_score_tiempo(dias_desde_email):
    """
    Calcula score de tiempo (0-100).
    Óptimo: 3-5 días = 100
    Aceptable: 1-7 días = 50-100
    Malo: >14 días = 0
    """
    if dias_desde_email < 1:
        return 20  # Muy pronto
    elif 3 <= dias_desde_email <= 5:
        return 100  # Óptimo
    elif 1 <= dias_desde_email < 3:
        return 70  # Un poco pronto
    elif 5 < dias_desde_email <= 7:
        return 80  # Todavía bien
    elif 7 < dias_desde_email <= 14:
        return 40  # Se enfrió
    else:
        return 0  # Demasiado tarde

def inferir_email_status(row):
    """
    Infiere el estado del email (para simulación si no hay datos reales).
    
    En producción, esto vendría de herramientas como:
    - Google Analytics (clicks)
    - Mailgun/SendGrid (opens, clicks, bounces)
    - HubSpot/Zoho (engagement tracking)
    
    Por ahora, simulamos basado en tier + probabilidades.
    """
    tier = row.get('tier', 'tier_4')
    status = row.get('status', 'sent')
    
    if status == 'failed' or status == 'bounced':
        return 'bounced'
    
    # Simulación de engagement por tier (basado en proyecciones)
    if tier == 'tier_1':
        rand = np.random.random()
        if rand < 0.25:
            return 'opened_no_click'
        elif rand < 0.32:
            return 'clicked_no_demo'
        else:
            return 'not_opened'
    
    elif tier == 'tier_2':
        rand = np.random.random()
        if rand < 0.20:
            return 'opened_no_click'
        elif rand < 0.25:
            return 'clicked_no_demo'
        else:
            return 'not_opened'
    
    elif tier == 'tier_3':
        rand = np.random.random()
        if rand < 0.15:
            return 'opened_no_click'
        elif rand < 0.19:
            return 'clicked_no_demo'
        else:
            return 'not_opened'
    
    else:  # tier_4
        rand = np.random.random()
        if rand < 0.10:
            return 'opened_no_click'
        else:
            return 'not_opened'

# ============================================================================
# CARGA Y PREPARACIÓN DE DATOS
# ============================================================================

print("="*80)
print("📞 GENERADOR DE LISTA PRIORIZADA DE LLAMADAS")
print("="*80)
print(f"\n⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Cargar farmacias
df_farmacias = pd.read_csv(FARMACIAS_FILE)
print(f"\n✅ Cargadas {len(df_farmacias)} farmacias")

# Verificar si existe tracking (si no, usar datos simulados)
if TRACKING_FILE.exists():
    print(f"✅ Cargando tracking desde: {TRACKING_FILE}")
    df_tracking = pd.read_csv(TRACKING_FILE)
    df_tracking['timestamp'] = pd.to_datetime(df_tracking['timestamp'])
    print(f"   → {len(df_tracking)} emails registrados")
else:
    print("⚠️  No hay tracking real. Generando lista basada en segmentación...")
    # Crear tracking simulado basado en segmentación
    # (En producción, esto se haría después de ejecutar main.py)
    df_tracking = pd.DataFrame()

# ============================================================================
# CALCULAR SEGMENTACIÓN SI NO EXISTE TRACKING
# ============================================================================

if df_tracking.empty:
    print("\n🔍 Calculando segmentación Tier 1-4 (no hay tracking disponible)...")
    
    from main import FarmaciaAnalyzer
    
    analyzer = FarmaciaAnalyzer()
    
    df_farmacias['priority_data'] = df_farmacias.apply(
        analyzer.calculate_priority_score, axis=1
    )
    df_farmacias['priority_score'] = df_farmacias['priority_data'].apply(lambda x: x['score'])
    df_farmacias['priority_tier'] = df_farmacias['priority_data'].apply(lambda x: x['tier'])
    
    # Simular que ya enviamos emails (para generar lista de llamadas)
    df_tracking = df_farmacias.copy()
    df_tracking['timestamp'] = datetime.now() - timedelta(days=4)  # Simulamos envío hace 4 días
    df_tracking['status'] = 'sent'
    df_tracking['tier'] = df_tracking['priority_tier']
    
    print(f"   ✅ Segmentadas {len(df_tracking)} farmacias")

# ============================================================================
# PREPARAR DATOS PARA PRIORIZACIÓN
# ============================================================================

print("\n🎯 Preparando datos para priorización...")

# Merge tracking con datos de farmacias
if 'email' in df_tracking.columns:
    df = df_tracking.merge(
        df_farmacias[['email', 'name', 'phone', 'provincia', 'rating', 'reviews', 'site']],
        on='email',
        how='left',
        suffixes=('', '_farm')
    )
else:
    df = df_tracking.copy()

# Limpiar teléfonos
df['phone_clean'] = df['phone'].apply(limpiar_telefono)
df['tiene_telefono'] = df['phone_clean'].notna()

# Calcular días desde email
if 'timestamp' in df.columns:
    ahora = datetime.now()
    df['dias_desde_email'] = (ahora - pd.to_datetime(df['timestamp'])).dt.days
else:
    df['dias_desde_email'] = 4  # Default

# Inferir email status
df['email_status'] = df.apply(inferir_email_status, axis=1)

print(f"   ✅ {len(df)} registros preparados")
print(f"   📞 {df['tiene_telefono'].sum()} farmacias con teléfono disponible")

# ============================================================================
# CALCULAR SCORE DE PRIORIZACIÓN
# ============================================================================

print("\n📊 Calculando scores de priorización...")

# Score por tier (40%)
df['score_tier'] = df['tier'].map(TIER_WEIGHTS).fillna(0) * 0.4

# Score por email status (30%)
df['score_status'] = df['email_status'].map(STATUS_WEIGHTS).fillna(0) * 0.3

# Score por tiempo (20%)
df['score_tiempo'] = df['dias_desde_email'].apply(calcular_score_tiempo) * 0.2

# Score por disponibilidad de teléfono (10%)
df['score_telefono'] = df['tiene_telefono'].astype(int) * 100 * 0.1

# Score total (0-100)
df['priority_score_llamada'] = (
    df['score_tier'] + 
    df['score_status'] + 
    df['score_tiempo'] + 
    df['score_telefono']
)

# Filtrar: solo farmacias con teléfono
df_llamadas = df[df['tiene_telefono']].copy()

# Ordenar por score (mayor a menor)
df_llamadas = df_llamadas.sort_values('priority_score_llamada', ascending=False)

print(f"   ✅ {len(df_llamadas)} farmacias válidas para llamar")

# ============================================================================
# ASIGNAR CATEGORÍAS DE PRIORIDAD
# ============================================================================

def asignar_categoria_prioridad(score):
    if score >= 80:
        return '🔥 PRIORIDAD 1 - Llamar HOY'
    elif score >= 60:
        return '⚡ PRIORIDAD 2 - Esta semana'
    elif score >= 40:
        return '📞 PRIORIDAD 3 - Próxima semana'
    else:
        return '⏳ PRIORIDAD 4 - Si sobra tiempo'

df_llamadas['categoria_prioridad'] = df_llamadas['priority_score_llamada'].apply(
    asignar_categoria_prioridad
)

# Añadir recomendación de producto
def recomendar_producto(row):
    tier = row.get('tier', 'tier_4')
    tiene_web = str(row.get('site', '')).strip().lower() not in ('', 'null', 'none', 'nan')
    
    if tier in ['tier_1', 'tier_2'] and tiene_web:
        return 'DIGITAL (Google + Reputación)'
    elif tier == 'tier_3' and tiene_web:
        return 'PEDIDOS DIRECTOS (+ Digital opcional)'
    else:
        return 'PEDIDOS DIRECTOS (sin web)'

df_llamadas['producto_recomendado'] = df_llamadas.apply(recomendar_producto, axis=1)

# ============================================================================
# GENERAR ESTADÍSTICAS
# ============================================================================

print("\n" + "="*80)
print("📈 ESTADÍSTICAS DE LA LISTA")
print("="*80)

print(f"\n📊 Distribución por Prioridad:")
for cat in ['🔥 PRIORIDAD 1 - Llamar HOY', 
            '⚡ PRIORIDAD 2 - Esta semana',
            '📞 PRIORIDAD 3 - Próxima semana',
            '⏳ PRIORIDAD 4 - Si sobra tiempo']:
    count = len(df_llamadas[df_llamadas['categoria_prioridad'] == cat])
    print(f"   {cat}: {count} farmacias")

print(f"\n📊 Distribución por Tier:")
for tier in ['tier_1', 'tier_2', 'tier_3', 'tier_4']:
    count = len(df_llamadas[df_llamadas['tier'] == tier])
    print(f"   {tier}: {count} farmacias")

print(f"\n📊 Distribución por Email Status:")
for status in df_llamadas['email_status'].unique():
    count = len(df_llamadas[df_llamadas['email_status'] == status])
    print(f"   {status}: {count} farmacias")

# ============================================================================
# EXPORTAR A EXCEL
# ============================================================================

print(f"\n💾 Exportando a Excel: {OUTPUT_FILE}")

# Seleccionar y ordenar columnas para Excel
columnas_export = [
    'categoria_prioridad',
    'priority_score_llamada',
    'name',
    'phone_clean',
    'email',
    'provincia',
    'tier',
    'email_status',
    'dias_desde_email',
    'rating',
    'reviews',
    'producto_recomendado',
    'site'
]

# Renombrar para claridad
df_export = df_llamadas[columnas_export].copy()
df_export.columns = [
    'Prioridad',
    'Score',
    'Farmacia',
    'Teléfono',
    'Email',
    'Provincia',
    'Tier',
    'Estado Email',
    'Días desde email',
    'Rating',
    'Reseñas',
    'Producto Recomendado',
    'Web'
]

# Exportar con formato
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_export.to_excel(writer, sheet_name='Lista Llamadas', index=False)
    
    # Obtener workbook y worksheet para formatear
    workbook = writer.book
    worksheet = writer.sheets['Lista Llamadas']
    
    # Ajustar anchos de columna
    worksheet.column_dimensions['A'].width = 35
    worksheet.column_dimensions['B'].width = 10
    worksheet.column_dimensions['C'].width = 30
    worksheet.column_dimensions['D'].width = 15
    worksheet.column_dimensions['E'].width = 30
    worksheet.column_dimensions['F'].width = 12
    worksheet.column_dimensions['G'].width = 10
    worksheet.column_dimensions['H'].width = 20
    worksheet.column_dimensions['I'].width = 18
    worksheet.column_dimensions['J'].width = 10
    worksheet.column_dimensions['K'].width = 10
    worksheet.column_dimensions['L'].width = 35
    worksheet.column_dimensions['M'].width = 30

print(f"   ✅ Exportadas {len(df_export)} farmacias")

# ============================================================================
# GENERAR RESUMEN ADICIONAL
# ============================================================================

print("\n📊 Generando hoja de resumen...")

# Crear resumen por prioridad y tier
resumen = df_llamadas.groupby(['categoria_prioridad', 'tier']).agg({
    'name': 'count',
    'priority_score_llamada': 'mean',
    'rating': 'mean',
    'reviews': 'mean'
}).round(2)

resumen.columns = ['Cantidad', 'Score Promedio', 'Rating Promedio', 'Reseñas Promedio']

# Exportar resumen en segunda hoja
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl', mode='a') as writer:
    resumen.to_excel(writer, sheet_name='Resumen')

# ============================================================================
# GENERAR INFORME FINAL
# ============================================================================

print("\n" + "="*80)
print("✅ LISTA DE LLAMADAS GENERADA CORRECTAMENTE")
print("="*80)

print(f"\n📁 Archivo: {OUTPUT_FILE}")
print(f"\n📞 Próximos pasos:")
print(f"   1. Abrir Excel: {OUTPUT_FILE.absolute()}")
print(f"   2. Filtrar por 'PRIORIDAD 1' → Llamar HOY")
print(f"   3. Usar argumentario: ARGUMENTARIO_LLAMADAS.md")
print(f"   4. Registrar resultados en: data/tracking/llamadas_log.csv")

print("\n💡 Tips:")
print("   - Mejores horarios: Martes-Jueves, 10:00-12:00h")
print("   - Duración óptima: 2-4 minutos")
print("   - Objetivo: Agendar demo de 15 minutos")

# Proyección de conversión
prioridad_1 = len(df_llamadas[df_llamadas['categoria_prioridad'] == '🔥 PRIORIDAD 1 - Llamar HOY'])
prioridad_2 = len(df_llamadas[df_llamadas['categoria_prioridad'] == '⚡ PRIORIDAD 2 - Esta semana'])

demos_proyectadas = int(prioridad_1 * 0.15 + prioridad_2 * 0.10)
ventas_proyectadas = int(demos_proyectadas * 0.70 * 0.30)

print(f"\n📈 Proyección de resultados:")
print(f"   - Prioridad 1+2: {prioridad_1 + prioridad_2} llamadas")
print(f"   - Demos esperadas: {demos_proyectadas} (15% conversión)")
print(f"   - Ventas esperadas: {ventas_proyectadas} (30% close rate)")
print(f"   - Ingresos potenciales: €{ventas_proyectadas * 1000:,}")

print("\n" + "="*80 + "\n")
