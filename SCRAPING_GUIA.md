#!/usr/bin/env python3
"""
🚀 EMAIL MARKETING + WHATSAPP CAMPAIGN - FARMACIAS ESPAÑA
Sistema completo para recopilar teléfonos de farmacias y contactarlas vía WhatsApp

ESTRUCTURA:
===========
campaign/
    - main.py: Configuración de campaña de email marketing
    - email_sender.py: Motor de envío SMTP
    
scrapers/
    - maps_scraper.py: Scraping de Google Maps (PRODUCCIÓN)
    - diagnostico.py: Verificar que Chrome y Maps funcionan
    - whatsapp_contact_manager.py: Gestionar contactos para WhatsApp
    
ARCHIVOS DE DATOS:
==================
- farmacias_españa_whatsapp.csv: Resultado principal (Provincia, CP, Nombre, Dirección, Telefonos, Web, Fecha, Contactado)
- logs_whatsapp/: Logs detallados del scraping (por día)
- blacklist.csv: Emails a excluir (para campaña de email)
- contactos.csv: Contactos de prueba

INSTALACIÓN:
============
1. Crear entorno virtual:
   python -m venv .venv

2. Activar (Windows):
   .\.venv\Scripts\Activate.ps1

3. Instalar dependencias:
   pip install -r requirements.txt

FLUJO DE TRABAJO:
=================

### FASE 1: Diagnóstico (Verificar que todo funciona)
   python scrapers/diagnostico.py
   
   ✅ Genera 3 screenshots para verificar:
      - Chrome se inicia
      - Google Maps carga
      - Se pueden buscar farmacias
      - Se encuentran resultados

### FASE 2: Scraping de Teléfonos (Recopilar datos)
   1. Editar maps_scraper.py:
      - MODO_PRUEBA = True  (para 3 CPs de Madrid)
      - MODO_PRUEBA = False (para todas las provincias)
      - PROVINCIAS_A_SCRAPEAR = ['Madrid'] (puedes limitar)
   
   2. Ejecutar:
      python scrapers/maps_scraper.py
   
   3. Resultado:
      - farmacias_españa_whatsapp.csv (datos extraídos)
      - logs_whatsapp/scraping_YYYY-MM-DD.log (progreso detallado)

### FASE 3: Gestionar Contactos (Rastrear progreso)
   # Ver estadísticas generales
   python scrapers/whatsapp_contact_manager.py stats
   
   # Exportar 50 contactos sin contactar de una provincia
   python scrapers/whatsapp_contact_manager.py exportar Madrid 50
   
   # Marcar como contactados (después de enviar WhatsApp)
   python scrapers/whatsapp_contact_manager.py marcar '+34666666666,+34777777777'

### FASE 4: Contactar por WhatsApp
   1. Exportar contactos con: whatsapp_contact_manager.py exportar
   2. Enviar mensajes WhatsApp manualmente o con bot
   3. Registrar teléfonos contactados
   4. Marcar en CSV: whatsapp_contact_manager.py marcar <TELEFONOS>

CONFIGURACIÓN MAPS_SCRAPER.PY:
===============================
- MODO_PRUEBA: True = Solo 3 CPs | False = Todas las provincias
- PROVINCIAS_A_SCRAPEAR: Lista de provincias a scrapear
- OUTPUT_FILE: Archivo CSV de salida
- LOGS_DIR: Carpeta de logs

ESTRATEGIA ANTI-BLOQUEO:
========================
✅ Delays aleatorios entre búsquedas (2-4 seg)
✅ Pausa entre códigos postales (8-12 seg)
✅ Pausa entre provincias (2-3 minutos)
✅ Límite de 15 scrolls por búsqueda
✅ Uso de undetected-chromedriver

Si Google bloquea:
- Espera 24 horas
- Intenta con otra IP/VPN
- Reduce MODO_PRUEBA a True para probar con menos datos

COLUMNAS DEL CSV PRINCIPAL:
===========================
Provincia       → Nombre de la provincia (Madrid, Barcelona, etc)
CP              → Código postal (28001, 28002, etc)
Nombre          → Nombre de la farmacia
Direccion       → Dirección completa
Telefonos       → Teléfono(s) encontrado(s) separados por ;
Web             → URL del sitio web (si existe)
Fecha_Extraccion→ Timestamp de extracción
Contactado      → No/Sí (marcado después de enviar WhatsApp)

TROUBLESHOOTING:
================
❌ "can't open file maps_scraper.py"
   → Asegúrate de estar en C:\Users\angel.martinez\Desktop\ProyectosNQ\email_marketing

❌ ModuleNotFoundError: No module named 'undetected_chromedriver'
   → pip install -r requirements.txt

❌ Chrome no se abre o cuelga
   → Ejecuta diagnostico.py para verificar
   → Cierra todas las instancias de Chrome
   → Reinicia la terminal

❌ Google Maps no carga / sin resultados
   → Espera 24 horas (Google bloqueó la IP)
   → Prueba con VPN
   → Revisa screenshot de diagnóstico.py

PRÓXIMOS PASOS:
===============
1. Ejecutar diagnostico.py ✓
2. Probar scraping en MODO_PRUEBA=True ✓
3. Verificar CSV y logs
4. Escalar a todas las provincias (MODO_PRUEBA=False)
5. Contactar por WhatsApp con whatsapp_contact_manager.py

NOTAS:
======
- El script funcionaba correctamente en macOS
- Adaptado para Windows con undetected-chromedriver
- Sistema de logs detallado para debugging
- CSV ordenado por provincia + CP para control
- Compatible con automatización vía WhatsApp Business API

AUTOR: Angel Martínez
FECHA: Enero 2026
"""

# Si ejecutan este archivo, mostrar este texto
if __name__ == "__main__":
    with open(__file__, 'r', encoding='utf-8') as f:
        print(f.read())
