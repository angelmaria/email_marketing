# Campañas de Email Marketing — Envío desde Python

Este proyecto automatiza el envío de campañas de email (orientado a farmacias) con plantillas HTML, control de lista negra (blacklist), límites anti‑bloqueo y soporte de múltiples emails por fila en el CSV de contactos.

## Descripción
- Envío por SMTP (Gmail) con plantilla HTML.
- Marcado de envíos por campaña para evitar duplicados.
- Soporte de varios correos en una misma fila (`Email` separados por `;`).
- Blacklist para excluir destinatarios que solicitan baja.
- Retardos aleatorios y pausas por lotes para reducir riesgo de bloqueo.
- Imágenes incrustadas en el correo (CID) para máxima compatibilidad en clientes de email.

## Estructura
- `email_sender.py`: Lógica central de cargas, filtros, envío, marcado y reintentos.
- `main.py`: Credenciales, configuración de tiempos, asunto, plantilla y lanzamiento de campaña.
- `TEMPLATES/email_camp_1.html`: Plantilla HTML con variables y enlaces de acción.
- `IMAGENES/`: Activos gráficos usados en la plantilla (se adjuntan inline por CID).
- `contacts.csv`: Fuente de destinatarios (email).
- `blacklist.csv`: Emails a excluir.
- `logs/`: Carpeta para logs de email.
- **`scrapers/maps_scraper.py`**: Scraper de Google Maps para extraer farmacias con nombre, dirección, teléfono y web.
- **`scrapers/whatsapp_contact_manager.py`**: Gestor de contactos para campañas WhatsApp (marcar como contactadas, estadísticas, exportar).
- **`farmacias_madrid_completo.csv`**: CSV generado por el scraper con todas las farmacias de Madrid.
- **`logs_madrid_scraping/`**: Logs detallados del scraping.

## Requisitos
- Python 3.9+ (probado en Windows).
- SMTP Gmail: `smtp.gmail.com:587` con contraseña de aplicación (no la contraseña normal).
- Sin dependencias externas adicionales.

## Uso Rápido
1. Coloca `contacts.csv` y (opcional) `blacklist.csv` en la carpeta `EMAIL`.
2. Revisa `TEMPLATES/email_camp_1.html` (placeholders: `{nombre}`, `{empresa}`, `{random_hash}`).
3. Asegura que `IMAGENES/` contiene:
   - `KPI.jpg`, `asistente_gestion.jpg`, `consejo_farmaceutico.jpg`, `digital.jpg`
4. Edita credenciales y campaña en `main.py`:
   - `SENDER_EMAIL`, `SENDER_PASSWORD` (contraseña de aplicación de Gmail)
   - `CAMPAIGN_ID`, `SUBJECT`, `HTML_TEMPLATE` (ej: `TEMPLATES/email_camp_1.html`)
5. Ejecuta:

```bash
python main.py
```

## Scraping de Farmacias (Google Maps)

### Google Maps Scraper
Script para extraer farmacias de Google Maps con contactos completos.

#### Uso
```bash
python scrapers/maps_scraper.py
```

#### Características
- Extrae: **Nombre, Dirección, Teléfono(s), Web, Provincia, CP**
- Modo COMPLETO: Scrapeea todos los CPs de Madrid (28001-28055)
- Detecta y captura **teléfonos móviles** (prefijos 6XX, 7XX)
- Sistema de logs detallado con timestamp
- Esperas aleatorias anti-detección
- CSV de salida: `farmacias_madrid_completo.csv`

#### Configuración
Edita las siguientes variables en el script si necesitas ajustar:

```python
# Cambiar a modo prueba (solo primeros 3 CPs)
MODO_PRUEBA = True  # False para scraping completo

# Provincias disponibles (descomentar la que necesites)
PROVINCIAS_A_SCRAPEAR = ['Madrid']  # Cambiar por otra provincia

# Archivos de salida
OUTPUT_FILE = 'farmacias_madrid_completo.csv'
LOGS_DIR = Path('logs_madrid_scraping')
```

#### Requisitos del Scraper
- Python 3.9+
- ChromeDriver (automático con `undetected_chromedriver`)
- Dependencias en `requirements.txt`:
  - `undetected-chromedriver`
  - `selenium`

#### Estadísticas Generadas
El script muestra en consola:
- Total de farmacias encontradas
- Cantidad con teléfono
- Porcentaje de cobertura
- Archivo CSV guardado
- Ubicación de logs

### WhatsApp Contact Manager
Gestor para rastrear contactos y campañas de WhatsApp.

#### Uso
```bash
# Ver estadísticas generales
python scrapers/whatsapp_contact_manager.py stats

# Exportar contactos sin contactar (todos, límite 50)
python scrapers/whatsapp_contact_manager.py exportar

# Exportar contactos de una provincia específica
python scrapers/whatsapp_contact_manager.py exportar Madrid 100

# Marcar farmacias como contactadas
python scrapers/whatsapp_contact_manager.py marcar "+34666666666,+34777777777"
```

#### Características
- **Estadísticas**: Total, con teléfono, contactadas, sin contactar (por provincia)
- **Exportar**: Genera CSV temporal con contactos pendientes
- **Marcar**: Marca como "Sí" en columna `Contactado` los teléfonos procesados
- Filtrado por provincia opcional
- Límites personalizables en exportación

#### Archivo de entrada
Espera `farmacias_madrid_completo.csv` (generado por el scraper) con columnas:
- `Provincia`, `CP`, `Nombre`, `Direccion`, `Telefonos`, `Web`, `Fecha_Extraccion`, `Contactado`

#### Uso Recomendado
1. Ejecuta el scraper para generar `farmacias_madrid_completo.csv`
2. Usa `exportar` para obtener lotes de contactos a procesar
3. Contacta vía WhatsApp o llamada telefónica
4. Marca como contactadas con `marcar` incluyendo los teléfonos procesados
5. Ejecuta `stats` para monitorear progreso



## Formato de `contacts.csv` (Email)
- Columnas mínimas esperadas: `Nombre`, `Email`.
- La columna `Email` acepta múltiples direcciones separadas por `;`.
- El script marca la fila con la columna `enviado_{CAMPAIGN_ID}` = `si` y añade `fecha_enviado_{CAMPAIGN_ID}`.
  - Nota: Al marcar la fila, si había varios emails en esa fila, estos no se reintentarán en la siguiente ejecución (diseño intencional para simplicidad con CSV).

## Formato de `farmacias_madrid_completo.csv` (Scraper)
- Columnas generadas automáticamente:
  - `Provincia`: Provincia de la farmacia
  - `CP`: Código postal
  - `Nombre`: Nombre de la farmacia
  - `Direccion`: Dirección completa desde Google Maps
  - `Telefonos`: Teléfono(s) separados por `;` (puede incluir móviles 6XX, 7XX)
  - `Web`: URL del sitio web (si disponible)
  - `Fecha_Extraccion`: Timestamp del scraping
  - `Contactado`: Estado de contacto (`No`, `Sí`) para rastreo con WhatsApp Contact Manager

## Blacklist (`blacklist.csv`)
- Estructura con cabecera `email` y una línea por correo, en minúsculas.
- El enlace de baja en la plantilla envía un correo; la adición a blacklist es manual (se puede automatizar con un endpoint/servicio si se desea).

## Limitadores y Anti‑Bloqueo
- `CONFIG` en `main.py` controla:
  - `min_delay`/`max_delay`: espera aleatoria entre envíos.
  - `batch_size`/`batch_delay`: pausa larga tras cada lote.
- `MAX_DAILY_LIMIT`: tope diario de seguridad (Gmail ~500/día; usar margen, p. ej., 450).

## Imágenes en el Email (CID)
- La plantilla referencia imágenes con CID: `cid:kpi_img`, `cid:asistente_img`, `cid:consejo_img`, `cid:digital_img`.
- `email_sender.py` adjunta automáticamente los ficheros de `IMAGENES/` a estos CID si existen.
- En navegadores (Live Server) los CID no se renderizan; verás las imágenes correctamente en el email real.

## Reintentos y Errores SMTP
- Si ocurre una desconexión (por ejemplo "Server not connected"), el envío reintenta automáticamente hasta 2 veces con una pausa breve.
- Para reducir desconexiones, evita esperas demasiado largas entre correos y mantén límites razonables.

## Personalización de la Plantilla
- CTA, asunto y copy pueden ajustarse en `TEMPLATES/email_camp_1.html` y `main.py`.
- El footer incluye el enlace a Healthfinder.
- Enlaces de acción:
  - Baja: `mailto:...subject=BAJA`
  - CTA Demo/Prueba: `mailto:` con texto prellenado (día y franja horaria).

## Buenas Prácticas de Seguridad
- No subas `contacts.csv` a repos públicos.
- Usa siempre contraseña de aplicación en Gmail.
- Considera separar activos públicos (imágenes) en un repositorio independiente si prefieres URLs públicas en vez de CID.

## Pruebas
- Puedes usar `concatos.csv` (datos de prueba) para validaciones sin afectar a contactos reales.

## Solución de Problemas

### Email
- Python 3.12 y `distutils`: si ves `ModuleNotFoundError: No module named 'distutils'`,
  asegúrate de instalar dependencias con `uv pip install -r requirements.txt`.
  Usamos versiones compatibles en `requirements.txt`.
- "0 correos a enviar": revisa que `enviado_{CAMPAIGN_ID}` no sea `si` en las filas objetivo.
- Encoding CSV: el cargador intenta `utf-8` y cae en `latin-1` si hace falta.
- Imágenes no visibles en navegador: es normal con CID; verifica con un envío real.

### Scraper de Google Maps
- **"ModuleNotFoundError: No module named 'undetected_chromedriver'"**: 
  Ejecuta `pip install -r requirements.txt` para instalar dependencias del scraper.
- **Chrome/ChromeDriver no encontrado**: 
  El paquete `undetected_chromedriver` descarga automáticamente el driver compatible. Si falla, reinicia el script.
- **Sin resultados en búsqueda**: 
  Google Maps puede bloquearte temporalmente si scrapeeas muy rápido. El script incluye esperas aleatorias; intenta de nuevo después de 10 minutos.
- **Pocos teléfonos capturados**: 
  Google Maps no siempre muestra teléfono en la ficha. Si solo ves ~10% con móvil, es normal (mayoría son fijos 91X).
- **Error "Server not connected" durante scraping**: 
  Conexión perdida con Chrome. El script reintenta; si persiste, reduce `max_scrolls` en el código.

### WhatsApp Contact Manager
- **"❌ No existe farmacias_madrid_completo.csv"**: 
  El script espera ese nombre exacto generado por el scraper. Ejecuta primero: `python scrapers/maps_scraper.py`
- **Columna 'Contactado' vacía**: 
  Después de scraping, esta columna se inicializa en `No`. Usa `marcar` para actualizarla.
- **Exportar genera archivo vacío**: 
  Revisa que existan contactos sin procesar: `python scrapers/whatsapp_contact_manager.py stats`

---

## Flujo Completo: De Scraping a Contacto WhatsApp

1. **Scraping de farmacias**
   ```bash
   python scrapers/maps_scraper.py
   ```
   Genera: `farmacias_madrid_completo.csv` con todas las farmacias y sus contactos.

2. **Revisar estadísticas iniciales**
   ```bash
   python scrapers/whatsapp_contact_manager.py stats
   ```
   Muestra cuántas farmacias hay, cuántas con teléfono, y breakdown por provincia.

3. **Exportar lote de contactos para procesar**
   ```bash
   python scrapers/whatsapp_contact_manager.py exportar Madrid 50
   ```
   Genera: `contactos_pendientes_YYYYMMDD_HHMMSS.csv` con 50 contactos de Madrid sin procesar.

4. **Contactar vía WhatsApp/Llamada**
   Procesa manualmente los contactos del lote exportado.

5. **Marcar como contactadas**
   ```bash
   python scrapers/whatsapp_contact_manager.py marcar "+34666666666,+34777777777"
   ```
   Actualiza la columna `Contactado` a `Sí` para los teléfonos procesados.

6. **Verificar progreso**
   ```bash
   python scrapers/whatsapp_contact_manager.py stats
   ```
   Confirma cuántas más faltan por contactar.

7. **Repetir pasos 3-6** hasta completar todas las farmacias.

---
¿Sugerencias o mejoras? Abre un issue interno o comenta en el propio proyecto.
