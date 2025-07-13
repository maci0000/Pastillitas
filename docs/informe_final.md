# Análisis y Desarrollo del Buscador de Medicamentos

> ### Enlace a la Aplicación Funcional
> La aplicación está desplegada en un servidor externo y se puede acceder desde cualquier dispositivo copiando y pegando la siguiente URL en un navegador:
> 
> **`https://79259f59-89c3-4c6f-8713-7eb1b6153d02-00-daplll22n1wu.kirk.replit.dev/`**

---

## 1. Metodología General del Proyecto
El proyecto se estructuró en cuatro fases principales, abarcando desde la recolección de datos hasta la puesta en producción de una herramienta interactiva.

1.  **Fase 1: Extracción de Datos (Web Scraping):** Se desarrollaron scripts en Python con la librería `Selenium` para automatizar la navegación y extracción de datos de dos sitios web de farmacias peruanas.
2.  **Fase 2: Procesamiento y Unificación de Datos:** Los datos crudos (raw data) obtenidos se procesaron, limpiaron y unificaron en un único dataset coherente utilizando la librería `Pandas`.
3.  **Fase 3: Desarrollo de la Aplicación Web:** Se construyó el motor de la aplicación con el framework `Flask`, que sirve como backend para la lógica de búsqueda y la integración con APIs externas.
4.  **Fase 4: Despliegue y Acceso Público:** La aplicación final se desplegó en la plataforma `Replit` para garantizar su disponibilidad y acceso a través de un enlace web público.

---

## 2. Fase de Extracción de Datos (Web Scraping)
Se implementaron dos scrapers distintos, cada uno adaptado a las particularidades del sitio web objetivo.

### 2.1. Scraper para 'Boticas y Salud'
*   **Tecnología:** Selenium con el driver `geckodriver` para controlar Firefox.
*   **Estrategia de Extracción:**
    1.  Navegación a la URL del catálogo de medicamentos.
    2.  Implementación de un bucle de **scroll infinito** para forzar la carga dinámica de todos los productos en la página. El script simula el desplazamiento del usuario hasta que la altura de la página deja de aumentar.
    3.  Una vez cargados todos los productos, se extraen los datos de cada "tarjeta de producto" (nombre, precio y principio activo) utilizando selectores CSS.
*   **Fragmento de Código Clave (Scroll Infinito):**
```python
# Bucle para simular el scroll y cargar todos los productos
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2) # Pausa para permitir la carga
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break # Se detiene si ya no hay más contenido
    last_height = new_height
```

---

### 2.1. Scraper para 'Hogar y Salud'
*   **Tecnología:** Selenium + Firefox (geckodriver)
*   **Estrategia de Extracción:**
    1.  Se identifico una estructura de paginacion, luego se implemento un bucle que imcrementa el numero de pagina hasta no encontrar mas productos.
    2.  En cada pagina de listado, se extraen los enlaces individuales de cada producto.
    3.  El script visita cada enlace de producto en una nueva pestaña  para acceder a la pagina de detalle.
    4.  Extrae nombre, precio y principio activo (de la pestaña “Composición”).
*   **Fragmento de Código Clave (Paginacion y visita a detalle):**
```python
# Bucle para iterar a través de las páginas del catálogo
while True:
    driver.get(base_url.format(page))
    enlaces = driver.find_elements(By.CSS_SELECTOR, "h3.wd-entities-title a")
    if not enlaces:
        break
    # abrir cada enlace, extraer y cerrar
    page += 1
```
---

## 3. Fase de Extracción de Datos (Web Scraping)
El script responde de esta fase toma los datos crudos y los prepara para la aplicacion

*   **Libreria Principal:** `Pandas`
*   **Proceso:**
    1. Carga de dos archivos CSV generados por los scrapers.
    2. Añadir una columna fuente a cada Dataframe para identificar el origen.
    3. Concatenar ambos Dataframes en uno solo usando pd.concat()
    4. Realizar una limpieza de datos esencial.
    5. Guardar el DataFrame limpio y unificado.

---

## 4. Fase de Desarrollo de la Aplicación Web
Componente      Descripción
Flask       	Microframework de Python utilizado para construir el backend y gestionar las rutas.
Pandas	        Al iniciar la aplicación, se carga el CSV unificado en un DataFrame para realizar búsquedas locales en memoria.
Requests	    Librería utilizada para realizar la petición HTTP a la API de OpenFDA.
Deep-Translator	Se utiliza para traducir al español los resultados en inglés de la API.
HTML / Jinja2	Se implementó una renderización del lado del servidor. Flask y Jinja2 inyectan los resultados directamente en el HTML antes de enviarlo al navegador.

---

## 5. Fase de Despliegue en Replit
Para hacer la aplicación accesible públicamente, se eligió la plataforma Replit.

*   **Entorno Contenerizado:** Replit ejecuta el proyecto en un contenedor, instalando las dependencias de requirements.txt.
*   **Exposición de Puertos:** Al ejecutar Flask con host='0.0.0.0', Replit detecta el puerto abierto y lo redirige a una URL pública.
*   **Ciclo de Vida "Dormir/Despertar":** La aplicación se "duerme" tras un período de inactividad y se "despierta" automáticamente en la siguiente visita.

