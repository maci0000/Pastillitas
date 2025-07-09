from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
import pandas as pd
import os
import time

# Configuración
geckodriver_path = r"C:\geckodriver-v0.36.0-win64\geckodriver.exe"
firefox_binary_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"

options = FirefoxOptions()
options.binary_location = firefox_binary_path
options.add_argument("--headless")

service = FirefoxService(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

# Navegar a la página
driver.get("https://www.boticasysalud.com/tienda/catalogo/medicinasytratamientos")
time.sleep(5)

# Scroll hasta que no se carguen más tarjetas nuevas
scroll_pause_time = 3
max_intentos = 15
intentos = 0
ultimas_tarjetas = 0

while intentos < max_intentos:
    tarjetas = driver.find_elements(By.CSS_SELECTOR, "div.product-card__information")
    total_tarjetas = len(tarjetas)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

    tarjetas_nuevas = driver.find_elements(By.CSS_SELECTOR, "div.product-card__information")
    nuevas_count = len(tarjetas_nuevas)

    if nuevas_count == ultimas_tarjetas:
        intentos += 1
    else:
        intentos = 0  # Se encontraron nuevas, reiniciar intentos
    
    ultimas_tarjetas = nuevas_count
    print(f"🔽 Scroll #{intentos} - Productos encontrados: {nuevas_count}")

print(f"✅ Productos totales encontrados: {ultimas_tarjetas}")

# Extracción
nombre_comercial = []
precios = []
principio_activo = []

for tarjeta in tarjetas_nuevas:
    try:
        nombre = tarjeta.find_element(By.CSS_SELECTOR, "div.product-card__name").text.strip()
    except:
        nombre = "No encontrado"

    try:
        precio_txt = tarjeta.find_element(By.CSS_SELECTOR, "div.product__summary-new-price").text.strip()
        precio_txt = precio_txt.replace("S/", "").replace(",", ".")
        precio = float(precio_txt)
    except:
        precio = 0.0

    try:
        posible_desc = tarjeta.find_elements(By.CSS_SELECTOR, "div.product-card__description")
        principio = "No encontrado"
        for desc in posible_desc:
            txt = desc.text.strip()
            if any(x in txt.lower() for x in ['mg', 'ml', '%']) or any(c.isdigit() for c in txt):
                principio = txt
                break
    except:
        principio = "No encontrado"

    nombre_comercial.append(nombre)
    precios.append(precio)
    principio_activo.append(principio)

# Cerrar navegador
driver.quit()

# Guardar CSV
df = pd.DataFrame({
    "Producto": nombre_comercial,
    "precio": precios,
    "PrincipioActivo": principio_activo,
    "farmacia": "Boticas y Salud"
})

output_path = "comparador_web/data/boticas_salud.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"📦 Total productos guardados: {len(df)}")
print(f"💾 Archivo: {output_path}")
