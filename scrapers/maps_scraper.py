import time
import csv
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN ---
OUTPUT_FILE = 'farmacias_madrid_free.csv'
# Generamos códigos postales de Madrid (28001 a 28055 aprox)
CIUDADES_O_ZONAS = [f"Farmacia en Madrid {cp}" for cp in range(28001, 28056)]
# Si quieres añadir barrios específicos, puedes hacerlo:
# CIUDADES_O_ZONAS.extend(["Farmacia en Madrid Centro", "Farmacia en Madrid Barrio Salamanca"])

def random_sleep(min_s=1, max_s=3):
    time.sleep(random.uniform(min_s, max_s))

def init_driver():
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # No uses headless en Maps o te detectan rápido
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options=options)
    return driver

def scrape_google_maps():
    driver = init_driver()
    
    # Preparamos el CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nombre', 'Direccion', 'Web', 'Busqueda_Origen'])

    try:
        for zona in CIUDADES_O_ZONAS:
            print(f"📍 Buscando: {zona}")
            driver.get('https://www.google.com/maps')
            random_sleep(2, 4)

            # 1. Aceptar Cookies (Solo la primera vez si salta)
            try:
                btns = driver.find_elements(By.TAG_NAME, "button")
                for btn in btns:
                    if "Aceptar todo" in btn.text or "Accept all" in btn.text:
                        btn.click()
                        random_sleep()
                        break
            except:
                pass

            # 2. Buscar en la caja de búsqueda
            try:
                search_box = driver.find_element(By.ID, "searchboxinput")
                search_box.clear()
                search_box.send_keys(zona)
                search_box.send_keys(Keys.ENTER)
                random_sleep(3, 5)
            except Exception as e:
                print(f"Error en caja de búsqueda: {e}")
                continue

            # 3. Detectar barra lateral y hacer Scroll
            # La clase de la barra lateral cambia, pero suele tener role="feed"
            try:
                # Esperamos que cargue el feed
                wait = WebDriverWait(driver, 10)
                # Buscamos el feed por el atributo role (es más estable que las clases)
                feed = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
                
                print("   🔄 Haciendo scroll para cargar resultados...")
                # Scroll loop
                last_height = 0
                max_scroll_attempts = 20 # Ajusta según necesidad (Maps suele topar en 120 resultados)
                
                for _ in range(max_scroll_attempts):
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    random_sleep(1, 2)
                    new_height = driver.execute_script("return arguments[0].scrollHeight", feed)
                    
                    # Si detectamos el mensaje de "Has llegado al final"
                    if "Has llegado al final" in driver.page_source:
                        break
                    
                    if new_height == last_height:
                        # Intento extra por si acaso está cargando lento
                        random_sleep(2, 3)
                        new_height = driver.execute_script("return arguments[0].scrollHeight", feed)
                        if new_height == last_height:
                            break
                    last_height = new_height
                
                print("   ✅ Scroll completado.")

            except Exception as e:
                print(f"   ⚠️ No se pudo hacer scroll o encontrar resultados: {e}")
                continue

            # 4. Extraer enlaces de cada tarjeta
            # Los elementos de la lista suelen ser 'a' con href que contiene /maps/place/
            listing_links = driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] > div > div > a")
            
            # Filtramos solo los que son enlaces a sitios (tienen href)
            urls_to_visit = []
            for a in listing_links:
                href = a.get_attribute('href')
                if href and "/maps/place/" in href:
                    urls_to_visit.append(href)
            
            # Eliminamos duplicados
            urls_to_visit = list(set(urls_to_visit))
            print(f"   🎯 Encontradas {len(urls_to_visit)} farmacias en esta zona. Extrayendo datos...")

            # 5. Visitar cada farmacia individualmente para sacar la web
            # (Esto es necesario porque la web no siempre sale en la lista previa)
            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for index, url in enumerate(urls_to_visit):
                    try:
                        driver.get(url)
                        # Esperar un poco a que cargue la ficha
                        random_sleep(1.5, 3) 
                        
                        # Extraer Nombre
                        try:
                            nombre = driver.find_element(By.TAG_NAME, "h1").text
                        except:
                            nombre = "Desconocido"

                        # Extraer Dirección (Botón con data-item-id="address")
                        try:
                            direccion = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').get_attribute("aria-label")
                            direccion = direccion.replace("Dirección: ", "")
                        except:
                            direccion = ""

                        # Extraer WEB (El santo grial)
                        web = ""
                        try:
                            # Buscamos el botón de sitio web. Suele tener data-item-id="authority"
                            web_btn = driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                            web = web_btn.get_attribute('href')
                        except:
                            # A veces no es data-item-id="authority", buscamos por aria-label que contenga "sitio web"
                            try:
                                btns = driver.find_elements(By.TAG_NAME, "a")
                                for b in btns:
                                    label = b.get_attribute("aria-label")
                                    if label and ("sitio web" in label.lower() or "website" in label.lower()):
                                        web = b.get_attribute("href")
                                        break
                            except:
                                pass

                        if web:
                            print(f"      [Found] {nombre} -> {web}")
                            writer.writerow([nombre, direccion, web, zona])
                        else:
                            print(f"      [No Web] {nombre}")

                    except Exception as e:
                        print(f"      ❌ Error en ficha: {e}")
                        # Si falla mucho, reiniciamos driver
                        continue

    except KeyboardInterrupt:
        print("🛑 Detenido por el usuario.")
    
    finally:
        driver.quit()
        print("🏁 Proceso finalizado.")

if __name__ == "__main__":
    scrape_google_maps()