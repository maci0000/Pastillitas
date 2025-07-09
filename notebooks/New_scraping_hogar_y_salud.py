from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.common.exceptions import WebDriverException
import pandas as pd
import os
import time

output_path = "data/hogarysalud_raw_data.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

options = ChromeOptions()
options.add_argument("--headless=new")  
options.add_argument("--start-maximized") 
options.add_argument("--disable-gpu") 
options.add_argument("--no-sandbox") 
options.add_argument("--disable-dev-shm-usage") 

try:
    print(" Iniciando Selenium para controlar Google Chrome...")
    driver = webdriver.Chrome(options=options)
    print(" Navegador Chrome iniciado correctamente.")

except WebDriverException as e:
    print(" Error iniciando Chrome. Revisa estos puntos:")
    print("1. Asegúrate de tener Google Chrome instalado.")
    print("2. Ten conexión a internet la primera vez para que Selenium descargue el driver.")
    print("3. Actualiza Selenium: pip install --upgrade selenium")
    print("\nError original:", e)
    exit()


base_url = "https://www.hogarysalud.com.pe/c/salud-y-bienestar/page/{}/"
page = 1

productos, precios, principios = [], [], []

while True:
    print(f"\n Procesando página {page}...")
    try:
        driver.get(base_url.format(page))
        time.sleep(2)

        enlaces_productos = driver.find_elements(By.CSS_SELECTOR, "h3.wd-entities-title a")
        if not enlaces_productos:
            print(" No se encontraron más productos. Fin del scraping.")
            break

        urls_a_visitar = [enlace.get_attribute("href") for enlace in enlaces_productos]
        
        for url_producto in urls_a_visitar:
            try:
                driver.execute_script("window.open(arguments[0]);", url_producto)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(1.5)

                try:
                    nombre_elemento = driver.find_element(By.CSS_SELECTOR, "h1.product_title.entry-title")
                    nombre = nombre_elemento.text.strip()
                except:
                    nombre = "Nombre no encontrado"

                try:
                    precio_elemento = driver.find_element(By.CSS_SELECTOR, ".price .amount")
                    precio_texto = precio_elemento.text.replace("S/", "").replace(",", "").strip()
                    precio = float(precio_texto)
                except:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                try:
                    composicion_button = driver.find_element(By.ID, "tab-title-composicion_tab")
                    composicion_button.click()
                    time.sleep(1)
                    composicion_tab = driver.find_element(By.ID, "tab-composicion_tab")
                    principio = composicion_tab.text.strip()
                except:
                    principio = "No encontrado"
                
                nombre_limpio = nombre.replace('\n', ' ').replace('\r', ' ').replace(',', ';').strip()
                principio_limpio = principio.replace('\n', ' ').replace('\r', ' ').replace(',', ';').strip()

                productos.append(nombre_limpio)
                precios.append(precio)
                principios.append(principio_limpio)
                
                print(f"     Extraído: {nombre_limpio[:50]}... | S/ {precio}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e_producto:
                print(f" Error procesando un producto en {url_producto}: {e_producto}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

        df_temp = pd.DataFrame({
            "Producto": productos,
            "Precio": precios,
            "PrincipioActivo": principios
        })
        df_temp.to_csv(output_path, index=False, encoding="utf-8-sig", sep=';')
        print(f" Guardado parcial: {len(df_temp)} productos en total.")

        page += 1

    except Exception as e_pagina:
        print(f" Error fatal en la página {page}: {e_pagina}")
        break

print("\n Scraping completado. Cerrando navegador.")
driver.quit()