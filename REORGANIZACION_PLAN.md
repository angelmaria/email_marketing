# 📁 Reorganización de Estructura - Email Marketing Projects

## 🎯 Objetivo

Reorganizar `email_marketing/` para reflejar **3 proyectos distintos** con ciclos de vida diferentes:
1. **Proyecto fallido** (para referencia histórica)
2. **Proyecto en progreso** (scraper de teléfonos/WhatsApp)
3. **Proyecto nuevo** (Healthfinder Galicia)

---

## 📊 Estado Actual

```
email_marketing/
├── campaign/              ❌ Confuso (¿cuál es el proyecto?)
├── IMAGENES/
├── scrapers/
├── TEMPLATES/
└── HF/
```

**Problema**: No está claro qué proyecto es cada cosa. Todo mezclado.

---

## ✅ Estructura Propuesta

```
email_marketing/
│
├── 1_GMAIL_CAMPAIGNS_V1/           ← Proyecto 1: Gmail (FALLIDO - referencia)
│   ├── README.md                   (Por qué falló, lecciones aprendidas)
│   ├── main.py                     (Script original - ARCHIVADO)
│   ├── email_sender.py             (Reutilizable si necesario)
│   ├── requirements.txt
│   ├── data/
│   │   └── contactos_originales.csv
│   ├── templates/
│   │   └── email_camp_1.html       (4 productos original)
│   ├── IMAGENES/
│   └── logs/
│       └── campaign_tracking_*.csv (Histórico de envíos)
│
├── 2_WHATSAPP_SCRAPER/             ← Proyecto 2: Scraper (EN PROGRESO)
│   ├── README.md                   (Documentación del scraper)
│   ├── main.py                     (Orquestador del scraper)
│   ├── requirements.txt
│   ├── scrapers/
│   │   ├── maps_scraper.py         (Extrae datos de Google Maps)
│   │   └── whatsapp_contact_manager.py
│   ├── data/
│   │   ├── raw/                    (Datos sin procesar)
│   │   │   └── maps_extracts.json
│   │   └── processed/              (Datos procesados)
│   │       └── contacts_with_whatsapp.csv
│   └── logs/
│       └── scraper_*.log
│
├── 3_HF_CAMPAIGNS/                 ← Proyecto 3: Healthfinder (NUEVO - ACTIVO)
│   ├── README.md                   ✅ Ya creado
│   ├── main.py                     ✅ Ya creado
│   ├── config.py                   ✅ Ya creado
│   ├── requirements.txt            ✅ Ya creado
│   ├── .env.example                ✅ Ya creado
│   ├── data/
│   │   ├── farmacias_galicia.csv   (1,319 registros)
│   │   ├── resumen_provincia.csv
│   │   └── top_50.csv
│   ├── templates/
│   │   ├── digital_posicionamiento.html        ← Crear
│   │   └── pedidos_directos.html               ← Crear
│   ├── utils/
│   │   └── whatsapp_helper.py      (Para follow-up futuro)
│   └── logs/
│       ├── campaign_YYYYMMDD.log
│       └── campaign_tracking_YYYYMMDD.csv
│
└── DOCS/                           ← Centralizado: documentación común
    ├── ARQUITECTURA.md             (Decisiones de diseño)
    ├── LECCIONES_APRENDIDAS.md     (Qué funcionó, qué no)
    ├── EMAIL_MARKETING_GUIDE.md    (Best practices generales)
    └── MIGRATION_PLAN.md           (Cómo migrar entre proyectos)
```

---

## 🔄 Plan de Migración

### Paso 1: Crear estructura nueva

```bash
# Desde email_marketing/
mkdir -p 1_GMAIL_CAMPAIGNS_V1
mkdir -p 2_WHATSAPP_SCRAPER/{scrapers,data/{raw,processed},logs}
mkdir -p 3_HF_CAMPAIGNS/{templates,utils,logs}
mkdir -p DOCS
```

### Paso 2: Mover archivos existentes

```bash
# Proyecto 1 - Gmail (archivado)
mv campaign/* 1_GMAIL_CAMPAIGNS_V1/
mv TEMPLATES/email_camp_1.html 1_GMAIL_CAMPAIGNS_V1/templates/

# Proyecto 2 - WhatsApp Scraper (en progreso)
mv scrapers/* 2_WHATSAPP_SCRAPER/scrapers/

# Proyecto 3 - Healthfinder (ya está)
# (No mover nada - ya está en HF/)

# IMAGENES - ¿De dónde es?
# Si era para Gmail: mv IMAGENES 1_GMAIL_CAMPAIGNS_V1/
# Si es compartida: dejar en raíz con rename a IMAGENES_SHARED/
```

### Paso 3: Limpiar raíz

```bash
# Solo dejar:
- .git/
- .gitignore
- README.md (general del proyecto)
- requirements.txt (agrupa dependencias)
- 1_GMAIL_CAMPAIGNS_V1/
- 2_WHATSAPP_SCRAPER/
- 3_HF_CAMPAIGNS/
- DOCS/
```

---

## 📝 Archivos a Crear/Actualizar

### 1. `/DOCS/ARQUITECTURA.md`

```markdown
# Arquitectura Email Marketing

## Decisiones Tecnológicas

### Por qué Gmail falla:
- IP bloqueada tras reintentos en emails inválidos
- Tasa límite de 500/día es restrictiva
- Difícil de personalizar a escala

### Por qué HF es diferente:
- Email de empresa (no personal) = mejor reputation
- 2 productos vs 4 = menos fatiga de mensaje
- Enfoque en lead quality vs volumen

### Futuros pasos:
- SendGrid/Mailgun para escala real (>100K)
- WhatsApp para re-engagement
- SMS como fallback
```

### 2. `/DOCS/LECCIONES_APRENDIDAS.md`

```markdown
# Lecciones Aprendidas

## Proyecto 1: Gmail Campaign ❌

### Qué funcionó:
✅ Templates HTML responsivos
✅ Rate limiting básico
✅ Logging y tracking

### Qué falló:
❌ Gmail bloqueó IP tras 24h
❌ Muchos emails de baja calidad (info@dominio.es)
❌ 4 productos = sobrecarga de mensaje
❌ Sin verificación de email antes de enviar

### Recomendación:
→ Usar email de empresa
→ 2 productos máximo
→ Validar emails antes de campañas
→ Usar SendGrid para volumen

## Proyecto 2: WhatsApp Scraper ⏳

(En progreso)

## Proyecto 3: HF Galicia ✅

(En lanzamiento)
```

### 3. `/email_marketing/README.md` (raíz)

```markdown
# 📧 Email Marketing - Healthfinder

3 proyectos distintos, 3 estrategias distintas.

## 📁 Proyectos

1. **1_GMAIL_CAMPAIGNS_V1/** - Proyecto fallido (V1)
   - Status: ❌ Descontinuado
   - Razón: IP bloqueada, calidad de datos baja
   - Usar para: Referencia de qué NO hacer

2. **2_WHATSAPP_SCRAPER/** - Extractor de contactos
   - Status: ⏳ En progreso
   - Objetivo: Obtener teléfono/WhatsApp de farmacias
   - Próximo: Integrar con HF campaigns

3. **3_HF_CAMPAIGNS/** - Galicia Q1 2025 (ACTIVO)
   - Status: ✅ Lanzando
   - Objetivo: 1,300 farmacias, 2 productos
   - Owner: angel.martinez@novaquality.es

## 🚀 Quick Start

```bash
# Para correr HF Galicia:
cd 3_HF_CAMPAIGNS
python main.py
```

Ver README.md en cada carpeta para detalles.
```

---

## 🎯 Matriz de Dependencias

| Archivo | Usado por | Comentario |
|---------|-----------|-----------|
| `email_sender.py` | 1 + 3 | Reutilizable (refactorizar) |
| `templates/` | 1 + 3 | Separar por proyecto |
| `IMAGENES/` | 1 + 3 | Compartida o duplicada? |
| `scrapers/` | 2 | Solo para scraper |
| `config.py` | 3 | Específico HF |

---

## ⚡ Acciones Inmediatas

### HIGH PRIORITY

- [ ] Crear carpetas 1_GMAIL_CAMPAIGNS_V1, 2_WHATSAPP_SCRAPER, DOCS
- [ ] Mover archivos existentes
- [ ] Crear README en cada proyecto
- [ ] Actualizar .gitignore global

### MEDIUM PRIORITY

- [ ] Refactorizar `email_sender.py` para reutilizar en HF
- [ ] Documentar lecciones aprendidas en DOCS/
- [ ] Crear plantilla de `config.py` reutilizable

### LOW PRIORITY

- [ ] Migrar datos históricos de Gmail a archivo (500GB?)
- [ ] Automatizar limpieza de logs antiguos
- [ ] Crear CI/CD para validar emails antes de enviar

---

## 📊 Timeline

```
HOY (15 Ene):
  ✅ Crear estructura de carpetas
  ✅ Mover archivos existentes
  ✅ Documentación inicial

SEMANA 1:
  → Refactorizar email_sender.py
  → Crear DOCS/LECCIONES_APRENDIDAS.md
  → Lanzar HF dry-run

SEMANA 2-4:
  → HF Galicia producción (50/día)
  → Paralelo: WhatsApp scraper testing

MES 2:
  → Análisis de resultados
  → Decisión: Escalar o pivotar
```

---

## 📞 Soporte

Cualquier duda sobre la reorganización: `angel.martinez@novaquality.es`
