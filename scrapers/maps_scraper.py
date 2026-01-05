#!/usr/bin/env python3
"""
Google Maps Scraper - Farmacias España
Extrae: Nombre, Dirección, Teléfono y Web
Organiza por Provincia y Código Postal
Sistema de logs para rastrear progreso
"""

import time
import csv
import random
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

# --- CONFIGURACIÓN ---
OUTPUT_FILE = 'farmacias_españa_whatsapp.csv'
LOGS_DIR = Path('logs_whatsapp')
LOGS_DIR.mkdir(exist_ok=True)

# Provincias españolas con códigos postales
PROVINCIAS_CODIGOS = {
    'Madrid': list(range(28001, 28056)),
    'Barcelona': list(range(8000, 8100)),
    'Valencia': list(range(46000, 46100)),
    'Sevilla': list(range(41000, 41050)),
    'Málaga': list(range(29000, 29100)),
    'Bilbao': list(range(48000, 48050)),
    'Zaragoza': list(range(50000, 50050)),
    'Alicante': list(range(3000, 3100)),
    'Córdoba': list(range(14000, 14050)),
    'Murcia': list(range(30000, 30050)),
}

# MODO PRUEBA: Solo Madrid y primeros 3 CPs
MODO_PRUEBA = True
PROVINCIAS_A_SCRAPEAR = ['Madrid']

if MODO_PRUEBA:
    print("⚠️  MODO PRUEBA: Solo Madrid (primeros 3 CPs)")
    PROVINCIAS_CODIGOS['Madrid'] = list(range(28001, 28004))  # 28001, 28002, 28003
else:
    print("🚀 MODO COMPLETO: Todas las provincias")
    PROVINCIAS_A_SCRAPEAR = list(PROVINCIAS_CODIGOS.keys())[:3]  # Primeras 3

# --- FUNCIONES ---

def random_sleep(min_s=1, max_s=3):
    """Espera aleatoria para evitar detección."""
    time.sleep(random.uniform(min_s, max_s))

def init_driver():
    """Inicializa Chrome con opciones anti-detección."""
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Error inicializando Chrome: {e}")
        raise

def log_evento(evento_tipo, farmacia_nombre, telefono="", provincia="", cp=""):
    """Registra eventos en logs."""
    try:
        timestamp = datetime.now().isoformat()
        log_file = LOGS_DIR / f"scraping_{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {evento_tipo:15} | {farmacia_nombre:40} | {telefono:20} | {provincia:10} {cp}\n")
    except:
        pass

def extraer_telefono(driver):
    """Extrae teléfono(s) de la ficha de Google Maps."""
    telefonos = []
    
    try:
        # Buscar botón con data-item-id="phone"
        tel_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="phone"]')
        aria_label = tel_btn.get_attribute("aria-label")
        if aria_label:
            telefono = aria_label.replace("Teléfono: ", "").strip()
            if telefono:
                telefonos.append(telefono)
    except:
        pass
    
    try:
        # Buscar links tel: adicionales
        tel_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="tel:"]')
        for link in tel_links:
            tel = link.get_attribute('href').replace('tel:', '').strip()
            if tel and tel not in telefonos:
                telefonos.append(tel)
    except:
        pass
    
    return telefonos

def extraer_provincia_cp(direccion):
    """Intenta extraer provincia y CP de la dirección."""
    provincia = ""
    cp = ""
    try:
        for prov, codigos in PROVINCIAS_CODIGOS.items():
            if prov in direccion:
                provincia = prov
                for codigo in codigos:
                    if str(codigo) in direccion:
                        cp = str(codigo)
                        break
                if cp:
                    break
    except:
        pass
    return provincia, cp

def scrape_google_maps():
    """Función principal de scraping."""
    driver = init_driver()
    
    # Preparar CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Provincia', 'CP', 'Nombre', 'Direccion', 'Telefonos', 'Web', 'Fecha_Extraccion', 'Contactado'])
    
    total_farmacies = 0
    total_con_telefono = 0
    
    try:
        for provincia in PROVINCIAS_A_SCRAPEAR:
            print(f"\n{'='*70}")
            print(f"📍 PROVINCIA: {provincia.upper()}")
            print(f"{'='*70}")
            
            codigos_postales = PROVINCIAS_CODIGOS[provincia]
            
            for cp in codigos_postales:
                zona = f"Farmacia en {provincia} {cp}"
                print(f"\n  🔍 Buscando: {zona}")
                
                try:
                    driver.get('https://www.google.com/maps')
                    random_sleep(2, 4)
                    
                    # Aceptar cookies (primera vez)
                    try:
                        btns = driver.find_elements(By.TAG_NAME, "button")
                        for btn in btns:
                            btn_text = btn.text.strip()
                            if "Aceptar todo" in btn_text or "Accept all" in btn_text:
                                btn.click()
                                random_sleep(1, 2)
                                print(f"    ✅ Cookies aceptadas")
                                break
                    except:
                        pass  # Si no hay cookies, continuar
                    
                    # Búsqueda
                    try:
                        search_box = driver.find_element(By.ID, "searchboxinput")
                        search_box.clear()
                        search_box.send_keys(zona)
                        search_box.send_keys(Keys.ENTER)
                        random_sleep(3, 5)
                    except Exception as e:
                        print(f"    ❌ Error en búsqueda: {e}")
                        log_evento("ERROR_BUSQUEDA", zona, "", provincia, cp)
                        continue
                    
                    # Cargar resultados
                    try:
                        wait = WebDriverWait(driver, 10)
                        feed = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
                        
                        print(f"    🔄 Cargando resultados...")
                        last_height = 0
                        max_scrolls = 15
                        
                        for _ in range(max_scrolls):
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                            random_sleep(1, 2)
                            new_height = driver.execute_script("return arguments[0].scrollHeight", feed)
                            
                            if "Ha llegado al final" in driver.page_source or "Has llegado al final" in driver.page_source:
                                break
                            if new_height == last_height:
                                break
                            last_height = new_height
                        
                        print(f"    ✅ Scroll completado")
                        
                    except Exception as e:
                        print(f"    ⚠️  No se cargaron resultados: {e}")
                        log_evento("ERROR_SCROLL", zona, "", provincia, cp)
                        continue
                    
                    # Extraer enlaces
                    listing_links = driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] > div > div > a")
                    
                    urls_to_visit = []
                    for a in listing_links:
                        href = a.get_attribute('href')
                        if href and "/maps/place/" in href:
                            urls_to_visit.append(href)
                    
                    urls_to_visit = list(set(urls_to_visit))
                    print(f"    🎯 Encontradas {len(urls_to_visit)} farmacias")
                    
                    # Procesar cada farmacia
                    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        for idx, url in enumerate(urls_to_visit, 1):
                            try:
                                driver.get(url)
                                random_sleep(1.5, 3)
                                
                                # Nombre
                                nombre = "Desconocido"
                                try:
                                    nombre = driver.find_element(By.TAG_NAME, "h1").text
                                except:
                                    pass
                                
                                # Dirección
                                direccion = ""
                                try:
                                    dir_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                                    direccion = dir_btn.get_attribute("aria-label").replace("Dirección: ", "")
                                except:
                                    pass
                                
                                # 📱 Teléfono (CRÍTICO)
                                telefonos = extraer_telefono(driver)
                                telefonos_str = ";".join(telefonos) if telefonos else ""
                                
                                # Provincia/CP
                                prov_ext, cp_ext = extraer_provincia_cp(direccion)
                                prov_final = prov_ext if prov_ext else provincia
                                cp_final = cp_ext if cp_ext else str(cp)
                                
                                # Web
                                web = ""
                                try:
                                    web_btn = driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                                    web = web_btn.get_attribute('href')
                                except:
                                    try:
                                        btns = driver.find_elements(By.TAG_NAME, "a")
                                        for b in btns:
                                            label = b.get_attribute("aria-label")
                                            if label and ("sitio web" in label.lower() or "website" in label.lower()):
                                                web = b.get_attribute("href")
                                                break
                                    except:
                                        pass
                                
                                fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
                                
                                # Registrar y guardar
                                if telefonos:
                                    print(f"      ✅ {nombre[:40]} → {telefonos_str[:25]}")
                                    total_con_telefono += 1
                                    log_evento("ENCONTRADO", nombre, telefonos_str, prov_final, cp_final)
                                else:
                                    print(f"      ⚠️  {nombre[:40]} (sin teléfono)")
                                    log_evento("SIN_TELEFONO", nombre, "", prov_final, cp_final)
                                
                                writer.writerow([
                                    prov_final, cp_final, nombre, direccion,
                                    telefonos_str, web, fecha, "No"
                                ])
                                
                                total_farmacies += 1
                                
                            except Exception as e:
                                print(f"      ❌ Error: {str(e)[:50]}")
                                continue
                    
                    # Pausa entre CPs
                    random_sleep(8, 12)
                    
                except Exception as e:
                    print(f"  ❌ Error en zona {zona}: {e}")
                    log_evento("ERROR_ZONA", zona, "", provincia, cp)
                    continue
            
            # Pausa entre provincias
            if provincia != PROVINCIAS_A_SCRAPEAR[-1]:
                print(f"\n⏸️  Pausa 2-3 minutos entre provincias...")
                random_sleep(120, 180)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Detenido por el usuario")
    finally:
        driver.quit()
        
        # Estadísticas
        print(f"\n{'='*70}")
        print(f"🏁 SCRAPING COMPLETADO")
        print(f"{'='*70}")
        print(f"📊 ESTADÍSTICAS:")
        print(f"   - Total farmacias: {total_farmacies}")
        print(f"   - Con teléfono: {total_con_telefono}")
        if total_farmacies > 0:
            cobertura = (total_con_telefono / total_farmacies) * 100
            print(f"   - Cobertura: {cobertura:.1f}%")
        print(f"📁 CSV guardado: {OUTPUT_FILE}")
        print(f"📋 Logs en: {LOGS_DIR}/")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 GOOGLE MAPS SCRAPER - FARMACIAS ESPAÑA")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Modo: {'PRUEBA (Madrid x3 CPs)' if MODO_PRUEBA else 'PRODUCCIÓN'}")
    print("="*70)
    
    try:
        scrape_google_maps()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
