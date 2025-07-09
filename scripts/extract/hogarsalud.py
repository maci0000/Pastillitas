from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import os
import time

# ------------------------- CONFIGURACIÓN --------------------------

geckodriver_path = r"C:\geckodriver-v0.36.0-win64\geckodriver.exe"
firefox_binary_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"

output_path = "comparador_web/data/hogar_salud.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

options = FirefoxOptions()
options.binary_location = firefox_binary_path
options.add_argument("--headless")

try:
    service = FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 10)
except WebDriverException as e:
    print("Error iniciando el navegador:", e)
    exit()

# ------------------------- SCRAPING --------------------------

base_url = "https://www.hogarysalud.com.pe/c/salud-y-bienestar/page/{}/"
page = 1

nombre_comercial, precios, principio_activo = [], [], []

while True:
    print(f"\n🔄 Procesando página {page}...")
    try:
        driver.get(base_url.format(page))
        time.sleep(2)

        enlaces = driver.find_elements(By.CSS_SELECTOR, "h3.wd-entities-title a")
        if not enlaces:
            print("✅ No se encontraron más productos. Fin del scraping.")
            break

        for enlace in enlaces:
            try:
                nombre = enlace.text.strip()
                url_producto = enlace.get_attribute("href")

                driver.execute_script("window.open(arguments[0]);", url_producto)
                driver.switch_to.window(driver.window_handles[1])

                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".price .amount")))
                    precio_elemento = driver.find_element(By.CSS_SELECTOR, ".price .amount")
                    precio_texto = precio_elemento.text.replace("S/", "").replace(",", "").strip()
                    precio = float(precio_texto)
                except:
                    precio = None

                try:
                    composicion_button = driver.find_element(By.ID, "tab-title-composicion_tab")
                    composicion_button.click()
                    time.sleep(1)
                    composicion_tab = driver.find_element(By.ID, "tab-composicion_tab")
                    principio = composicion_tab.text.strip().replace("Composición", "")
                except:
                    principio = "No encontrado"

                # Guardar datos aunque falte composición o precio
                nombre_comercial.append(nombre)
                precios.append(precio if precio is not None else 0.0)
                principio_activo.append(principio)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as err:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

        df_temp = pd.DataFrame({
            "Producto": nombre_comercial,
            "precio": precios,
            "PrincipioActivo": principio_activo,
        })
        df_temp["farmacia"] = "Hogar y Salud"

        df_temp.to_csv(output_path, index=False, encoding="utf-8")
        print(f"💾 Guardado parcial: {len(df_temp)} productos")

        page += 1

    except Exception as e:
        print(f"❌ Error en página {page}: {e}")
        break

print("\n🎉 Scraping completado. Cerrando navegador.")
driver.quit()
