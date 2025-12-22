import smtplib
import csv
import time
import random
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import re
import html as html_lib
from pathlib import Path

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.assets_dir = Path(__file__).resolve().parent / "IMAGENES"
        # Permite desactivar imágenes inline para minimizar señales de spam
        self.disable_images = os.getenv('DISABLE_IMAGES', 'false').strip().lower() in ('1', 'true', 'yes')
        Path("logs").mkdir(exist_ok=True)

    def attach_inline_images(self, msg):
        """Adjunta imágenes inline (CID) si existen en la carpeta IMAGENES."""
        image_map = {
            "kpi_img": "KPI.jpg",
            "asistente_img": "asistente_gestion.jpg",
            "consejo_img": "consejo_farmaceutico.jpg",
            "digital_img": "digital.jpg",
        }

        for cid, filename in image_map.items():
            img_path = self.assets_dir / filename
            if not img_path.exists():
                continue
            try:
                with open(img_path, "rb") as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=img_path.name)
                    msg.attach(img)
            except Exception as e:
                print(f"⚠️ No se pudo adjuntar {filename}: {e}")

    def _strip_cid_images(self, html_content: str) -> str:
        """Elimina etiquetas <img> que referencian src="cid:*" para modo sin imágenes."""
        return re.sub(r'<img[^>]+src="cid:[^"]+"[^>]*>', '', html_content, flags=re.IGNORECASE)

    def _html_to_text(self, html_content: str) -> str:
        """Convierte HTML a texto plano básico para la parte 'plain'."""
        # Quitar scripts/estilos
        no_scripts = re.sub(r'<(script|style)[\s\S]*?>[\s\S]*?</\1>', '', html_content, flags=re.IGNORECASE)
        # Reemplazos sencillos de saltos de línea para bloques típicos
        block_breaks = re.sub(r'</(p|div|tr|li|h[1-6])\s*>', '\n', no_scripts, flags=re.IGNORECASE)
        # Quitar el resto de etiquetas
        text_only = re.sub(r'<[^>]+>', '', block_breaks)
        # Desescapar entidades HTML
        text_only = html_lib.unescape(text_only)
        # Normalizar espacios y líneas
        lines = [line.strip() for line in text_only.splitlines()]
        compact = '\n'.join([l for l in lines if l])
        return compact

    def load_blacklist(self, blacklist_file='blacklist.csv'):
        blacklist = set()
        if os.path.exists(blacklist_file):
            with open(blacklist_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('email'):
                        blacklist.add(row['email'].strip().lower())
        return blacklist

    def load_pending_contacts(self, csv_file='contactos.csv', campaign_col='enviado_c1'):
        contacts = []
        blacklist = self.load_blacklist()
        
        try:
            # Detección de encoding (utf-8 vs latin-1)
            try:
                file = open(csv_file, 'r', encoding='utf-8')
                sample = file.read(1024)
                file.seek(0)
                dialect = csv.Sniffer().sniff(sample)
            except UnicodeDecodeError:
                file = open(csv_file, 'r', encoding='latin-1')
                sample = file.read(1024)
                file.seek(0)
                dialect = csv.Sniffer().sniff(sample)

            reader = csv.DictReader(file, dialect=dialect)
            
            for row in reader:
                # Si ya se envió la campaña a esta fila (farmacia), la saltamos entera
                if row.get(campaign_col, '').lower() == 'si':
                    continue

                raw_emails = row.get('Email', '')
                if not raw_emails:
                    continue
                
                # --- CAMBIO IMPORTANTE: LOGICA MULTI-EMAIL ---
                # Separamos por punto y coma y limpiamos espacios
                email_list = [e.strip() for e in raw_emails.split(';') if e.strip()]
                
                # Iteramos sobre TODOS los emails encontrados en esa fila
                for individual_email in email_list:
                    primary_email = individual_email.lower()
                    
                    if not primary_email or '@' not in primary_email:
                        continue

                    # Verificar blacklist para este email concreto
                    if primary_email in blacklist:
                        print(f"🚫 Ignorando (Blacklist): {primary_email}")
                        continue
                    
                    # Normalizar nombre
                    nombre = row.get('Nombre', 'Farmacéutico').strip().title()
                    
                    # Añadimos este email específico a la lista de envíos
                    contact_clean = {
                        'email': primary_email,
                        'nombre': nombre,
                        'empresa': "tu farmacia", 
                        'row_data': row # Referencia a la fila original
                    }
                    contacts.append(contact_clean)
                
            file.close()

        except FileNotFoundError:
            print(f"Error: No se encuentra el archivo {csv_file}")
            
        return contacts

    def mark_as_sent(self, target_email, campaign_col, csv_file='contacts.csv'):
        rows = []
        fieldnames = []
        encoding_used = 'utf-8'

        try:
            file = open(csv_file, 'r', encoding='utf-8')
            sample = file.read(1024)
            file.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            encoding_used = 'utf-8'
        except UnicodeDecodeError:
            file = open(csv_file, 'r', encoding='latin-1')
            sample = file.read(1024)
            file.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            encoding_used = 'latin-1'

        reader = csv.DictReader(file, dialect=dialect)
        fieldnames = reader.fieldnames
        rows = list(reader)
        file.close()

        if campaign_col not in fieldnames:
            fieldnames.append(campaign_col)
            fieldnames.append(f"fecha_{campaign_col}")

        updated = False
        for row in rows:
            # Buscamos la fila que contenga este email (aunque haya otros en la misma celda)
            if target_email in row.get('Email', '').lower():
                # Marcamos la fila como enviada.
                # NOTA: Al marcar la fila, si el script se para bruscamente, 
                # los otros emails de esta misma fila no se enviarán en la próxima ejecución.
                # Es un compromiso aceptable para mantener la simplicidad del CSV.
                row[campaign_col] = 'si'
                row[f"fecha_{campaign_col}"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updated = True
                break 

        if updated:
            with open(csv_file, 'w', encoding=encoding_used, newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, dialect=dialect)
                writer.writeheader()
                writer.writerows(rows)

    def send_single_email(self, contact, subject, html_content, campaign_col, max_retries=2):
        try:
            # Estructura recomendada: multipart/related -> multipart/alternative (plain + html) + imágenes
            root = MIMEMultipart('related')
            alt = MIMEMultipart('alternative')
            root['From'] = f"Ángel Martínez <{self.sender_email}>"
            root['To'] = contact['email']
            root['Subject'] = subject
            # List-Unsubscribe para mejorar entregabilidad
            root['List-Unsubscribe'] = '<mailto:angel.martinez.nq@gmail.com?subject=BAJA>'

            body = html_content.replace('{nombre}', contact['nombre'])
            body = body.replace('{empresa}', contact['empresa'])

            if self.disable_images:
                body_to_send = self._strip_cid_images(body)
            else:
                body_to_send = body

            # Partes plain y html
            plain_part = MIMEText(self._html_to_text(body_to_send), 'plain', 'utf-8')
            html_part = MIMEText(body_to_send, 'html', 'utf-8')

            alt.attach(plain_part)
            alt.attach(html_part)
            root.attach(alt)

            # Adjuntar imágenes solo si no está desactivado
            if not self.disable_images:
                self.attach_inline_images(root)

            # --- RETRY LOGIC ---
            for attempt in range(max_retries + 1):
                try:
                    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                        server.starttls()
                        server.login(self.sender_email, self.sender_password)
                        server.sendmail(self.sender_email, contact['email'], root.as_string())
                    
                    print(f"✅ Enviado: {contact['email']} ({contact['nombre']})")
                    self.mark_as_sent(contact['email'], campaign_col)
                    return True
                
                except (smtplib.SMTPServerDisconnected, smtplib.SMTPException, ConnectionError) as e:
                    if attempt < max_retries:
                        print(f"⚠️ Desconexión detectada en {contact['email']}. Reintentando ({attempt + 1}/{max_retries})...")
                        time.sleep(5)  # Esperar 5s antes de reintentar
                    else:
                        raise e
            
            return True

        except Exception as e:
            print(f"❌ Error enviando a {contact['email']}: {e}")
            return False

    def launch_campaign(self, subject, html_file_path, config, campaign_col, daily_limit=450):
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_base = f.read()
        except FileNotFoundError:
            print(f"❌ Error: No se encuentra la plantilla HTML: {html_file_path}")
            return

        contacts = self.load_pending_contacts(campaign_col=campaign_col)
        total = len(contacts)
        print(f"🎯 Total de correos a enviar (incluyendo múltiples por farmacia): {total}")
        print(f"🛡️ Límite diario de seguridad configurado en: {daily_limit}")
        
        emails_sent_today = 0

        for i, contact in enumerate(contacts, 1):
            # --- PROTECCIÓN DIARIA ---
            if emails_sent_today >= daily_limit:
                print(f"\n🛑 LÍMITE DIARIO DE {daily_limit} ALCANZADO.")
                print("El script se detendrá por seguridad para evitar bloqueo de Gmail.")
                print("Puedes continuar mañana.")
                break

            current_html = html_base.replace("{random_hash}", str(random.getrandbits(128)))
            
            success = self.send_single_email(contact, subject, current_html, campaign_col)
            
            if success:
                emails_sent_today += 1

            # Lógica de espera
            if i < total and emails_sent_today < daily_limit:
                delay = random.randint(config['min_delay'], config['max_delay'])
                if i % config['batch_size'] == 0:
                    print(f"⏸️ Pausa larga anti-bloqueo...")
                    time.sleep(config['batch_delay'])
                else:
                    print(f"⏳ Esperando {delay}s...")
                    time.sleep(delay)