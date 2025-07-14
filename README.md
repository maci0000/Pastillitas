# 💊 Comparación de Precios de Medicinas en Farmacias Peruanas

## 🧠 Objetivo

Analizar y comparar los precios de medicamentos entre dos farmacias online en Perú para evaluar accesibilidad y disponibilidad, así como la descripción, indicaciÓn y uso de los medicamentos desde fuentes oficiales como la API de la FDA.

## 📌 Fuentes de datos

1. **Bienestar y Salud** – Web scraping de productos.
2. **Hogar y Salud** – Web scraping de productos.
3. **OpenFDA API** – Información complementaria de medicamentos.


## Ejecución Local (Para Desarrolladores y Evaluadores)

Cualquier persona puede ejecutar una copia de esta aplicación en su propia computadora. Esto es ideal para probar, modificar o evaluar el código sin depender de una conexión a internet o de la plataforma Replit. Los pasos son los siguientes:

1.  **Descargar el Código:** Clonar o descargar el repositorio completo desde GitHub.
2.  **Instalar Dependencias:** Asegurarse de tener Python instalado y ejecutar `pip install -r requirements.txt` en la terminal para instalar Flask, Pandas y las demás librerías necesarias.
3.  **Ubicar los Datos:** Colocar el archivo `medicamentos_unificados.csv` dentro de la carpeta `data/`. **Este paso es crucial**, ya que la aplicación necesita este archivo para funcionar.
4.  **Ejecutar el Servidor:** Correr el comando `python new_app.py` en la terminal.
5.  **Acceder a la Aplicación:** Abrir un navegador web y visitar la dirección local `http://127.0.0.1:5001`. La aplicación será completamente funcional.

## 🛠️ Herramientas

- Python
- Selenium
- BeautifulSoup, Requests
- Pandas, Matplotlib, Seaborn
- Jupyter Notebook
- Git y GitHub

## 📁 Estructura del proyecto

Ver estructura de carpetas en este repositorio.

## 👥 Integrantes

- Sean Huancani – @Sean-cristobal30
- Valeska Rodriguez – @maci0000


## 📈 Producto final

- Base de datos en `.csv` con nombre comercial, precio y principio activo por medicamento y farmacia.
- Extracción de datos desde la API.
- Visualizaciones sobre diferencias de precio y accesibilidad desde la página web.
