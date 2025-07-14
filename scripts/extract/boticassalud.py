from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

# Configuración
geckodriver_path = r"C:\geckodriver-v0.36.0-win64\geckodriver.exe"
firefox_binary_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
output_path = "raw_data/boticas_salud.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

options = FirefoxOptions()
options.binary_location = firefox_binary_path
# options.add_argument("--headless")  # Descomenta si quieres ver el navegador
service = FirefoxService(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Abrir catálogo
base_url = "https://www.boticasysalud.com"
driver.get(f"{base_url}/tienda/catalogo/medicinasytratamientos")
time.sleep(5)

productos = []
vistos = set()
scrolls = 0
enlaces_previos = 0

# Scroll infinito hasta que no aparezcan más productos
while True:
    enlaces = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/tienda/productos/"]')
    nuevos = 0

    for enlace in enlaces:
        href = enlace.get_attribute("href")
        if href in vistos:
            continue
        vistos.add(href)
        nuevos += 1

        # Nombre
        try:
            nombre = enlace.find_element(By.CSS_SELECTOR, "div.product-card__name").text.strip()
        except:
            nombre = "No encontrado"

        # Precio
        try:
            precio_txt = enlace.find_element(By.CSS_SELECTOR, "div.product__summary-new-price").text.strip()
            precio_txt = precio_txt.replace("S/", "").replace(",", ".").strip()
            if not precio_txt.replace(".", "", 1).isdigit():
                continue
            Precio = float(precio_txt)
        except:
            continue  # sin precio → no guardar

        # Ir al producto
        try:
            driver.execute_script("window.open(arguments[0]);", href)
            driver.switch_to.window(driver.window_handles[-1])
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product__spec")))
            time.sleep(1)

            # PRINCIPIO ACTIVO
            principio = "No encontrado"
            try:
                spec_btn = driver.find_element(By.CSS_SELECTOR, "div.product__spec")
                driver.execute_script("arguments[0].scrollIntoView(true);", spec_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", spec_btn)

                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.product__spec-even")))
                time.sleep(1)

                try:
                    spec_panel = driver.find_element(By.CSS_SELECTOR, "div.product__specifications")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", spec_panel)
                    time.sleep(1)
                except:
                    driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(1)

                filas = driver.find_elements(By.CSS_SELECTOR, "div.row.product__spec-even")
                for fila in filas:
                    try:
                        clave = fila.find_element(By.CSS_SELECTOR, "div.col-4").text.strip().lower()
                        valor = fila.find_element(By.CSS_SELECTOR, "div.col-8 div").text.strip()
                        if "principio activo" in clave:
                            principio = valor
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ No se encontró principio activo: {e}")

            productos.append({
                "Producto": nombre,
                "Precio": Precio,
                "PrincipioActivo": principio,
                "Farmacia": "Boticas y Salud"
            })

            print(f"✅ {len(productos)}. {nombre} | S/{Precio} | {principio}")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"⚠️ Error al cargar producto: {e}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            continue

    # Scroll si se encontraron nuevos productos
    if nuevos == 0:
        print("🛑 No se encontraron productos nuevos. Fin del scroll.")
        break

    scrolls += 1
    print(f"🔽 Scroll #{scrolls} | Nuevos productos encontrados: {nuevos}")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Guardar CSV
driver.quit()
df = pd.DataFrame(productos)
df.to_csv(output_path, index=False, encoding="utf-8")
print(f"\n📦 Total productos guardados: {len(df)}")
print(f"💾 Archivo: {output_path}")
