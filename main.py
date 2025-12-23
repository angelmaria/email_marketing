from email_sender import EmailSender

# --- TUS CREDENCIALES ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'angel.martinez.nq@gmail.com'
SENDER_PASSWORD = 'kybb tadp bkye oife' 

# --- CONFIGURACIÓN DE ENVÍO ---
CONFIG = {
    'min_delay': 30,
    'max_delay': 70,
    'batch_size': 40,
    'batch_delay': 300
}

# --- SEGURIDAD ---
# Gmail permite 500/día. Ponemos 450 para dejar margen a tus emails normales.
MAX_DAILY_LIMIT = 450 

# --- DEFINICIÓN DE LA CAMPAÑA ACTUAL ---
CAMPAIGN_ID = "c1" 
SUBJECT = "⚕️ 4 Herramientas para optimizar tu farmacia"
HTML_TEMPLATE = "templates/email_camp_1.html"
CONTACTS_FILE = "contactos.csv" # <--- Updated back to production file

if __name__ == "__main__":
    sender = EmailSender(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD)
    
    print(f"🚀 Iniciando campaña: {CAMPAIGN_ID}")
    print(f"📂 Plantilla: {HTML_TEMPLATE}")
    print(f"📋 Archivo contactos: {CONTACTS_FILE}")
    
    sender.launch_campaign(
        SUBJECT, 
        HTML_TEMPLATE, 
        CONFIG, 
        campaign_id=CAMPAIGN_ID, 
        daily_limit=MAX_DAILY_LIMIT,
        csv_file=CONTACTS_FILE # <--- Updating call
    )