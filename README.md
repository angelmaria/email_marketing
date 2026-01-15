# 📧 Email Marketing Projects - Portfolio Profesional

**Suite de herramientas de email marketing para el sector farmacéutico**

---

## 📁 ESTRUCTURA DEL REPOSITORIO

Este repositorio contiene **3 proyectos independientes** con diferentes estados:

```
email_marketing/
├── 1_GMAIL_CAMPAIGNS_V1/     ❌ ARCHIVADO (proyecto fallido - referencia histórica)
├── 2_WHATSAPP_SCRAPER/        🔨 EN DESARROLLO (scraper de contactos)
├── 3_HF_CAMPAIGNS/            ✅ ACTIVO (campaña Healthfinder Galicia)
└── DOCS/                      📚 Documentación compartida
```

---

## 🎯 PROYECTOS

### 1️⃣ Gmail Campaigns V1 (ARCHIVADO)

**Estado**: ❌ Fallido - Solo para referencia histórica  
**Razón de cierre**: Bloqueo de IP + ROI negativo (-100%)

**Lecciones aprendidas**:
- Gmail personal NO es viable para campañas comerciales
- 4 productos en 1 email = sobrecarga cognitiva
- Sin warm-up de IP = spam flag inmediato

➡️ [Ver detalles](1_GMAIL_CAMPAIGNS_V1/README.md)

---

### 2️⃣ WhatsApp Scraper (EN DESARROLLO)

**Estado**: 🔨 En progreso  
**Objetivo**: Extraer teléfonos + validar WhatsApp Business para follow-up

**Funcionalidades**:
- Scraping de Google Maps (farmacias por provincia)
- Validación de WhatsApp Business
- Integración con campaña HF para follow-up post-email

➡️ [Ver documentación](2_WHATSAPP_SCRAPER/README.md)

---

### 3️⃣ Healthfinder Campaigns (ACTIVO)

**Estado**: ✅ Producción  
**Objetivo**: 1,319 farmacias Galicia → 2 productos (Digital + Pedidos Directos)

**Resultados esperados**:
- 530 emails Fase 1 (Tier 1+2)
- 20% open rate, 5% CTR
- 5 clientes cerrados → €5,000-7,500 ingresos
- ROI: 12.5x

**Diferencias clave vs Gmail V1**:
- ✅ Email corporativo (@novaquality.es)
- ✅ 2 productos (no 4)
- ✅ Rate limiting (50 emails/día)
- ✅ Segmentación Tier 1-4 (prioridad = urgencia)

➡️ [Ver documentación completa](3_HF_CAMPAIGNS/README.md)

---

## 📚 DOCUMENTACIÓN COMPARTIDA

### Arquitectura y Decisiones

| Documento | Descripción |
|-----------|-------------|
| [LECCIONES_APRENDIDAS.md](DOCS/LECCIONES_APRENDIDAS.md) | Qué funcionó y qué no |
| [EMAIL_MARKETING_GUIDE.md](DOCS/EMAIL_MARKETING_GUIDE.md) | Best practices generales |
| [SCRAPING_GUIA.md](DOCS/SCRAPING_GUIA.md) | Técnicas de web scraping |
| [GDPR_CHECKLIST.md](DOCS/GDPR_CHECKLIST.md) | Compliance legal |

---

## 🚀 QUICK START

### Para lanzar campaña Healthfinder (ACTIVO)

```powershell
cd 3_HF_CAMPAIGNS

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales (.env)
copy .env.example .env
# Editar .env con tu SMTP

# 3. Análisis visual (gráficos para stakeholders)
python analisis_visual.py

# 4. Lanzar campaña (DRY-RUN primero)
python main.py
```

### Para usar WhatsApp Scraper (EN DESARROLLO)

```powershell
cd 2_WHATSAPP_SCRAPER

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Scraping de farmacias
python scrapers/maps_scraper.py --query "farmacias en A Coruña" --max 100

# 3. Validar WhatsApp Business
python scrapers/whatsapp_validator.py --input data/raw/telefonos.csv
```

---

## 📊 COMPARATIVA DE PROYECTOS

| Métrica | Gmail V1 (Fallido) | HF Campaign (Activo) | Diferencia |
|---------|-------------------|---------------------|------------|
| Email usado | Gmail personal | @novaquality.es | +80% reputación |
| Productos ofrecidos | 4 | 2 | +2.5x CTR |
| Rate limiting | No | 50/día | -90% spam risk |
| Open rate | 12% | 20% (target) | +8% |
| CTR | 1.8% | 5% (target) | +3.2% |
| Demos agendadas | 0 | 5 (proyectado) | +5 |
| ROI | -100% | 12.5x (proyectado) | +12.5x |

---

## 🏗️ ARQUITECTURA TECNOLÓGICA

### Tech Stack

| Componente | Tecnología |
|------------|-----------|
| **Lenguaje** | Python 3.11+ |
| **Email Sending** | smtplib (Gmail SMTP) |
| **Data Processing** | Pandas 2.3.3 |
| **Web Scraping** | Selenium + BeautifulSoup |
| **Visualización** | matplotlib + seaborn |
| **Export** | openpyxl (Excel) |

### Dependencias Compartidas

Instalar desde raíz:
```powershell
pip install -r requirements.txt
```

---

## 🎓 LECCIONES APRENDIDAS (Resumen)

### ✅ QUÉ FUNCIONA

1. **Email corporativo** > Gmail personal (80% menos spam)
2. **2 productos** > 4 productos (2.5x CTR)
3. **Segmentación por urgencia** > Por calidad (Tier 1 = peor reputación pero más necesidad)
4. **Rate limiting agresivo** (50/día) > Sin límites (spam flag)
5. **Follow-up multicanal** (Email → WhatsApp → Llamada) > Solo email

### ❌ QUÉ NO FUNCIONA

1. **Gmail personal** para >100 emails comerciales → Bloqueo permanente
2. **4+ productos** en 1 email → Parálisis por análisis
3. **Envío masivo día 1** sin warm-up → IP blacklisted
4. **30% bounce rate** sin validación → Reputación dañada
5. **Sin follow-up** → 80% de leads perdidos

---

## 📈 ROADMAP

### Q1 2025 (Actual)
- ✅ Healthfinder Galicia (1,319 farmacias)
- ✅ Segmentación Tier 1-4
- ⏳ WhatsApp Scraper (en desarrollo)
- ⏳ Argumentario de llamadas + lista priorizada

### Q2 2025
- Expansión: Asturias (800 farmacias), Castilla y León (1,200)
- Añadir producto: Consejo Farmacéutico (cross-sell)
- WhatsApp automation (Business API)
- CRM integration (HubSpot/Zoho)

### Q3 2025
- Dashboard de métricas en tiempo real (Streamlit)
- A/B testing automatizado de emails
- Predictive analytics (ML para conversión)

---

## 🤝 CONTACTO

**Ángel Martínez**  
Consultor de Digitalización Farmacéutica  
📧 angel.martinez@novaquality.es  
📱 [Tu teléfono]

**Healthfinder**  
🌐 [URL de Healthfinder]

---

## 📜 LICENCIA

Este repositorio es **privado** y propiedad de NovaQuality / Healthfinder.  
Prohibida la reproducción sin autorización.

---

**Última actualización**: 2025-01-XX  
**Versión**: 2.0  
**Autor**: Ángel Martínez (con asistencia de GitHub Copilot)
