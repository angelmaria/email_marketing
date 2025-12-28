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
- `contacts.csv`: Fuente de destinatarios.
- `blacklist.csv`: Emails a excluir.
- `logs/`: Carpeta reservada (salida principal por consola).

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

### Uso con uv (entornos gestionados)
- Requiere `uv` instalado.
- Este repo incluye `pyproject.toml` y `requirements.txt`.

1) Instala dependencias con uv usando `requirements.txt` (sin empaquetar el repo):

```bash
uv pip install -r requirements.txt
```

2) Ejecuta el scraper de Google Maps:

```bash
uv run scrapers/maps_scraper.py
```

Si prefieres el intérprete del venv directamente:

```bash
. .venv/bin/activate
python scrapers/maps_scraper.py
```

## Formato de `contacts.csv`
- Columnas mínimas esperadas: `Nombre`, `Email`.
- La columna `Email` acepta múltiples direcciones separadas por `;`.
- El script marca la fila con la columna `enviado_{CAMPAIGN_ID}` = `si` y añade `fecha_enviado_{CAMPAIGN_ID}`.
  - Nota: Al marcar la fila, si había varios emails en esa fila, estos no se reintentarán en la siguiente ejecución (diseño intencional para simplicidad con CSV).

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
- Python 3.12 y `distutils`: si ves `ModuleNotFoundError: No module named 'distutils'`,
  asegúrate de instalar dependencias con `uv pip install -r requirements.txt`.
  Usamos versiones compatibles en `requirements.txt`.
- "0 correos a enviar": revisa que `enviado_{CAMPAIGN_ID}` no sea `si` en las filas objetivo.
- Encoding CSV: el cargador intenta `utf-8` y cae en `latin-1` si hace falta.
- Imágenes no visibles en navegador: es normal con CID; verifica con un envío real.

---
¿Sugerencias o mejoras? Abre un issue interno o comenta en el propio proyecto.
