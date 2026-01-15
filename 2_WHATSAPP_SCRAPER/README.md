# 📱 WhatsApp Scraper (PROYECTO EN PROGRESO)

## 🎯 ESTADO: EN DESARROLLO

Scraper automatizado para extraer datos de farmacias desde Google Maps  
y validar disponibilidad de WhatsApp Business para follow-up.

---

## 📋 OBJETIVO

**Problema**: Muchas farmacias no responden emails → Necesitamos canal alternativo (WhatsApp).

**Solución**: Extraer números de teléfono desde Google Maps + validar WhatsApp Business.

**Use Case**: Integrar con campaña HF para follow-up post-email vía WhatsApp.

---

## 🚀 FUNCIONALIDADES

### 1. **Google Maps Scraper**

Extrae datos de farmacias desde Google Maps API:
- Nombre de farmacia
- Dirección completa
- Teléfono (fijo + móvil si disponible)
- Rating + número de reseñas
- Horarios de apertura
- Coordenadas GPS

### 2. **WhatsApp Business Validator**

Valida si un número de teléfono tiene WhatsApp Business activado:
- Usa API no oficial de WhatsApp Web (selenium)
- Detecta badge "Business Account"
- Extrae descripción del perfil

### 3. **Contact Manager**

Gestiona base de datos de contactos:
- Deduplicación (mismo teléfono = 1 contacto)
- Historial de interacciones
- Tags: email_sent, whatsapp_available, etc.

---

## 🛠️ INSTALACIÓN

### Requisitos

```powershell
# Python 3.11+
python --version

# Instalar dependencias
pip install -r requirements.txt
```

**requirements.txt**:
```
selenium==4.17.0
webdriver-manager==4.0.1
pandas==2.3.3
openpyxl==3.1.5
beautifulsoup4==4.12.3
requests==2.31.0
python-dotenv==1.0.0
```

### Configuración API

Crear `.env` en la raíz:

```env
# Google Maps API (opcional - si quieres usar oficial)
GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# WhatsApp Web (para scraping)
WHATSAPP_SESSION_PATH=./whatsapp_session

# Rate limiting
SCRAPER_DELAY_SECONDS=5
MAX_REQUESTS_PER_MINUTE=10
```

---

## ▶️ USO

### Opción 1: Scraping de Google Maps

```powershell
# Extraer farmacias de una ciudad
python scrapers/maps_scraper.py --query "farmacias en A Coruña" --max 100

# Output: data/raw/maps_extract_coruña.json
```

### Opción 2: Validar WhatsApp Business

```powershell
# Validar lista de teléfonos
python scrapers/whatsapp_validator.py --input data/raw/telefonos.csv

# Output: data/processed/contacts_with_whatsapp.csv
```

### Opción 3: Pipeline Completo

```powershell
# Scraping → Validación → Export
python main.py --provincia Galicia --validate-whatsapp

# Output:
# - data/processed/farmacias_galicia_full.csv
# - data/processed/contacts_whatsapp_business.csv
```

---

## 📊 OUTPUT

### Archivo CSV Generado

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `name` | Nombre de farmacia | "Farmacia López" |
| `phone` | Teléfono principal | "+34981234567" |
| `phone_mobile` | Móvil (si disponible) | "+34612345678" |
| `whatsapp_available` | ¿Tiene WhatsApp Business? | TRUE / FALSE |
| `whatsapp_profile_text` | Descripción del perfil | "Farmacia 24h en A Coruña" |
| `email` | Email (si disponible) | "info@farmacialopez.com" |
| `address` | Dirección completa | "Calle Real 123, A Coruña" |
| `rating` | Rating Google (0-5) | 4.3 |
| `reviews` | Número de reseñas | 87 |
| `coordinates` | GPS | "43.3713, -8.3960" |

---

## 🔧 COMPONENTES

### `scrapers/maps_scraper.py`

**Función**: Extrae datos de Google Maps.

**Métodos**:
- `search_pharmacies(query, max_results)`: Busca farmacias por query
- `extract_details(pharmacy_url)`: Extrae detalles de una farmacia
- `save_to_json(data, filename)`: Guarda resultados

**Limitaciones**:
- Google Maps rate limit: ~100 requests/hora (sin API key)
- Con API key: 25,000 requests/día (gratis)

### `scrapers/whatsapp_validator.py`

**Función**: Valida WhatsApp Business.

**Métodos**:
- `validate_phone(phone_number)`: Verifica WhatsApp en un número
- `batch_validate(phone_list)`: Valida lista completa
- `extract_profile_info(phone)`: Extrae bio del perfil

**Limitaciones**:
- Requiere sesión de WhatsApp Web iniciada manualmente (1ra vez)
- Rate limit: ~50 números/hora (para evitar ban)

### `main.py`

**Función**: Orquestador del pipeline completo.

**Workflow**:
1. Scraping de Google Maps
2. Limpieza de datos (deduplicación, validación)
3. Validación de WhatsApp Business (opcional)
4. Export a CSV/Excel

---

## 📈 MÉTRICAS DE PROGRESO

| Métrica | Actual | Target | Estado |
|---------|--------|--------|--------|
| Farmacias scraped | 0 | 1,319 | ⏳ Pendiente |
| WhatsApp validado | 0 | 800+ | ⏳ Pendiente |
| Tasa de éxito scraping | N/A | >95% | ⏳ Pendiente |
| Tiempo scraping (1,319) | N/A | <4h | ⏳ Pendiente |

---

## 🔗 INTEGRACIÓN CON HF CAMPAIGN

### Flujo de Trabajo Integrado

```
1. Email Campaign (HF)
   ├─ Email enviado
   ├─ 72h espera
   └─ Si no responde → Trigger WhatsApp

2. WhatsApp Scraper
   ├─ Verificar si tiene WhatsApp Business
   ├─ Si SÍ → Enviar mensaje personalizado
   └─ Si NO → Llamada telefónica (backup)

3. Follow-up Strategy
   ├─ WhatsApp: "Hola [Nombre], te envié email hace 3 días sobre..."
   ├─ Si lee y no responde → Llamada telefónica
   └─ Si no lee → Marcar como "No interesado"
```

### Script de Integración

```python
# En 3_HF_CAMPAIGNS/utils/whatsapp_helper.py
from scrapers.whatsapp_validator import WhatsAppValidator

def send_follow_up(pharmacy_data):
    validator = WhatsAppValidator()
    
    if validator.validate_phone(pharmacy_data['phone']):
        # Enviar mensaje por WhatsApp
        message = f"Hola {pharmacy_data['name']}, soy Ángel de Healthfinder..."
        validator.send_message(pharmacy_data['phone'], message)
    else:
        # Fallback: Llamada telefónica
        print(f"Sin WhatsApp: {pharmacy_data['name']} → Llamar")
```

---

## 🚧 ROADMAP

### Fase 1: Scraping Básico (ACTUAL)
- ✅ Estructura de carpetas creada
- ⏳ Implementar maps_scraper.py
- ⏳ Implementar whatsapp_validator.py
- ⏳ Testing con 50 farmacias (sample)

### Fase 2: Automatización (Q1 2025)
- ⏳ Scraping automático diario (cron job)
- ⏳ Notificaciones si nuevas farmacias detectadas
- ⏳ Dashboard de monitoreo (Streamlit)

### Fase 3: WhatsApp Automation (Q2 2025)
- ⏳ Integración con WhatsApp Business API (oficial)
- ⏳ Templates de mensajes aprobados
- ⏳ Auto-respuestas basadas en IA (GPT-4)

---

## ⚠️ CONSIDERACIONES LEGALES

### GDPR Compliance

- **Datos públicos**: Google Maps = datos públicamente accesibles
- **Consentimiento**: WhatsApp follow-up requiere opt-in previo (email = primer contacto con opt-out)
- **Derecho al olvido**: Implementar sistema de "No contactar más"

### WhatsApp Terms of Service

- **NO spam**: Max 1 mensaje/persona/campaña sin respuesta
- **Business API**: Para uso comercial a escala (>1,000 mensajes/mes)
- **Rate limiting**: Respetar límites (evitar ban permanente)

---

## 🤝 CONTRIBUIR

Este proyecto está activo. Mejoras bienvenidas:
- Optimización de rate limiting
- Bypass de CAPTCHAs en Google Maps
- Integración con CRM (HubSpot, Zoho)

---

## 📚 RECURSOS

- [Google Maps Scraping Guide](../DOCS/SCRAPING_GUIA.md)
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/business-management-api)
- [GDPR Compliance Checklist](../DOCS/GDPR_CHECKLIST.md)

---

**Estado**: EN DESARROLLO  
**Última actualización**: 2025-01-XX  
**Responsable**: Ángel Martínez
