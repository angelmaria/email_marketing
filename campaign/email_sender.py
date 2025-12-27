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
        self.assets_dir = Path(__file__).resolve().parent.parent / "IMAGENES"
        # Permite desactivar imágenes inline para minimizar señales de spam
        self.disable_images = os.getenv('DISABLE_IMAGES', 'false').strip().lower() in ('1', 'true', 'yes')
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.history_file = self.logs_dir / "sent_history.csv"
        
        # Inicializar archivo de historial si no existe
        if not self.history_file.exists():
            with open(self.history_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["campaign_id", "email", "timestamp", "status"])

    def _log(self, kind: str, text: str):
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            log_path = self.logs_dir / f"{kind}_{date}.log"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} | {text}\n")
        except Exception:
            pass

    def _read_csv_robust(self, filepath):
        """Lee un CSV intentando varias codificaciones."""
        if not os.path.exists(filepath):
            return []
        
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    # Leemos una muestra para detectar el dialecto
                    sample = f.read(2048)
                    f.seek(0)
                    dialect = csv.Sniffer().sniff(sample)
                    
                    reader = csv.DictReader(f, dialect=dialect)
                    return list(reader)
            except (UnicodeDecodeError, csv.Error):
                continue
                
        print(f"❌ Error: No se pudo leer {filepath} con codificaciones estándar.")
        return []

    def load_history(self, campaign_id):
        """Carga el historial de envíos exitosos para esta campaña."""
        sent_emails = set()
        if not self.history_file.exists():
            return sent_emails
            
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('campaign_id') == campaign_id and row.get('status') == 'sent':
                        sent_emails.add(row.get('email', '').strip().lower())
        except Exception as e:
            print(f"⚠️ Error leyendo historial: {e}")
            
        return sent_emails

    def mark_as_sent(self, campaign_id, email):
        """Registra un envío exitoso en el historial (append-only, super rápido)."""
        try:
            with open(self.history_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    campaign_id, 
                    email, 
                    datetime.now().isoformat(), 
                    'sent'
                ])
        except Exception as e:
            print(f"⚠️ Error guardando historial para {email}: {e}")

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
        return re.sub(r'<img[^>]+src="cid:[^"]+"[^>]*>', '', html_content, flags=re.IGNORECASE)

    def _html_to_text(self, html_content: str) -> str:
        no_scripts = re.sub(r'<(script|style)[\s\S]*?>[\s\S]*?</\1>', '', html_content, flags=re.IGNORECASE)
        block_breaks = re.sub(r'</(p|div|tr|li|h[1-6])\s*>', '\n', no_scripts, flags=re.IGNORECASE)
        text_only = re.sub(r'<[^>]+>', '', block_breaks)
        text_only = html_lib.unescape(text_only)
        lines = [line.strip() for line in text_only.splitlines()]
        compact = '\n'.join([l for l in lines if l])
        return compact

    def load_blacklist(self, blacklist_file='blacklist.csv'):
        blacklist = set()
        rows = self._read_csv_robust(blacklist_file)
        for row in rows:
            if row.get('email'):
                blacklist.add(row['email'].strip().lower())
        return blacklist

    def load_pending_contacts(self, campaign_id, csv_file='contactos.csv'):
        contacts = []
        blacklist = self.load_blacklist()
        sent_history = self.load_history(campaign_id)
        
        raw_rows = self._read_csv_robust(csv_file)
        
        if not raw_rows:
            print(f"Error: No se encontraron contactos o el archivo {csv_file} está vacío/dañado.")
            return []

        print(f"Total filas en CSV: {len(raw_rows)}")
        print(f"Emails ya enviados en esta campaña: {len(sent_history)}")

        for row_idx, row in enumerate(raw_rows):
            raw_emails = row.get('Email', '')
            if not raw_emails:
                continue
            
            # Separamos por punto y coma
            email_list = [e.strip() for e in raw_emails.split(';') if e.strip()]
            
            for email in email_list:
                clean_email = email.lower()
                
                # Validaciones
                if '@' not in clean_email:
                    continue
                if clean_email in blacklist:
                    # Solo verbose si quieres depurar
                    # print(f"🚫 Ignorando (Blacklist): {clean_email}") 
                    continue
                if clean_email in sent_history:
                    # Ya enviado
                    continue
                
                # Preparar objeto de contacto
                nombre = row.get('Nombre', 'Farmacéutico').strip().title()
                contact = {
                    'email': clean_email,
                    'nombre': nombre,
                    'empresa': "tu farmacia", 
                    'original_row': row
                }
                contacts.append(contact)
                
        return contacts

    def send_single_email(self, server, contact, subject, html_content, max_retries=1):
        """Envía un email usando una conexión SMTP ya abierta."""
        try:
            root = MIMEMultipart('related')
            alt = MIMEMultipart('alternative')
            root['From'] = f"Ángel Martínez <{self.sender_email}>"
            root['To'] = contact['email']
            root['Subject'] = subject
            root['List-Unsubscribe'] = '<mailto:angel.martinez.nq@gmail.com?subject=BAJA>'

            body = html_content.replace('{nombre}', contact['nombre'])
            body = body.replace('{empresa}', contact['empresa'])

            if self.disable_images:
                body_to_send = self._strip_cid_images(body)
            else:
                body_to_send = body

            plain_part = MIMEText(self._html_to_text(body_to_send), 'plain', 'utf-8')
            html_part = MIMEText(body_to_send, 'html', 'utf-8')

            alt.attach(plain_part)
            alt.attach(html_part)
            root.attach(alt)

            if not self.disable_images:
                self.attach_inline_images(root)

            server.sendmail(self.sender_email, contact['email'], root.as_string())
            
            print(f"✅ Enviado: {contact['email']} ({contact['nombre']})")
            self._log('sent', f"{contact['email']} | {contact['nombre']}")
            return True

        except Exception as e:
            print(f"❌ Fallo al enviar a {contact['email']}: {e}")
            self._log('error', f"{contact['email']} | {e}")
            return False

    def launch_campaign(self, subject, html_file_path, config, campaign_id, daily_limit=450, csv_file='contactos.csv'):
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_base = f.read()
        except FileNotFoundError:
            print(f"❌ Error: No se encuentra la plantilla HTML: {html_file_path}")
            return

        print("🔍 Analizando contactos y filtrando enviados...")
        contacts = self.load_pending_contacts(campaign_id=campaign_id, csv_file=csv_file)
        total = len(contacts)
        
        if total == 0:
            print("🎉 ¡Campaña completada! No hay contactos pendientes.")
            return

        print(f"🎯 Total de correos PENDIENTES de enviar: {total}")
        print(f"🛡️ Límite diario de seguridad configurado en: {daily_limit}")
        
        emails_sent_today = 0
        
        # --- CONEXIÓN SMTP PERSISTENTE ---
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                print("🔌 Conexión SMTP establecida exitosamente.")

                for i, contact in enumerate(contacts, 1):
                    # Chequeo de límites
                    if emails_sent_today >= daily_limit:
                        print(f"\n🛑 LÍMITE DIARIO DE {daily_limit} ALCANZADO.")
                        break

                    # Personalización hash
                    current_html = html_base.replace("{random_hash}", str(random.getrandbits(128)))
                    
                    # Intentar envío
                    try:
                        success = self.send_single_email(server, contact, subject, current_html)
                    except smtplib.SMTPServerDisconnected:
                        print("⚠️ Conexión perdida. Reconectando...")
                        server.connect(self.smtp_server, self.smtp_port)
                        server.starttls()
                        server.login(self.sender_email, self.sender_password)
                        success = self.send_single_email(server, contact, subject, current_html)

                    if success:
                        emails_sent_today += 1
                        self.mark_as_sent(campaign_id, contact['email'])
                    
                    # Lógica de espera
                    if i < total and emails_sent_today < daily_limit:
                        delay = random.randint(config['min_delay'], config['max_delay'])
                        if i % config['batch_size'] == 0:
                            print(f"⏸️ Pausa larga anti-bloqueo...")
                            time.sleep(config['batch_delay'])
                        else:
                            print(f"⏳ Esperando {delay}s...")
                            time.sleep(delay)

        except Exception as e:
            print(f"❌ Error fatal en la conexión SMTP o loop principal: {e}")
        finally:
            print(f"\n✅ Resumen de sesión: {emails_sent_today} emails enviados hoy.")