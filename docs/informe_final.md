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

### 2.2. Scraper para 'Hogar y Salud'
*   **Tecnología:** Selenium + Firefox (geckodriver)
*   **Estrategia de Extracción:**
    1.  Se identificó una estructura de paginación, luego se implementó un bucle que incrementa el número de página hasta no encontrar más productos.
    2.  En cada página de listado, se extraen los enlaces individuales de cada producto.
    3.  El script visita cada enlace de producto en una nueva pestaña para acceder a la página de detalle.
    4.  Extrae nombre, precio y principio activo (de la pestaña “Composición”).
*   **Fragmento de Código Clave (Paginación y visita a detalle):**
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

## 3. Fase de Unificación de Datos
El script de esta fase toma los datos crudos generados por los scrapers y los prepara para ser consumidos por la aplicación web.

*   **Librería Principal:** `Pandas`
*   **Proceso:**
    1.  Carga de los dos archivos CSV generados.
    2.  Añadir una columna `Farmacias` a cada DataFrame para identificar el origen de los datos.
    3.  Concatenar ambos DataFrames en uno solo usando la función `pd.concat()`.
    4.  Realizar una limpieza de datos esencial (eliminar duplicados, formatear precios, etc.).
    5.  Guardar el DataFrame limpio y unificado en `medicamentos_unificados.csv`.

---

## 4. Fase de Desarrollo de la Aplicación Web y la Interfaz de Usuario

Esta fase se centró en construir el núcleo funcional de la aplicación: un servidor web que procesa búsquedas, consulta fuentes de datos y presenta la información de manera clara.

### 4.1. Lógica del Backend (`app.py`)

El archivo `app.py` es el cerebro de la aplicación. Su flujo lógico es el siguiente:

**1. Búsqueda Local de Precios con Pandas:**
Se utiliza una máscara de `Pandas` para filtrar eficientemente el DataFrame cargado en memoria, realizando una búsqueda insensible a mayúsculas en dos columnas simultáneamente.

```python
# app.py - Fragmento de búsqueda de precios
query_lower = query.lower()
mask = (medicamentos_df['Productos'].str.lower().str.contains(query_lower, na=False)) | \
       (medicamentos_df['PrincipioActivo'].str.lower().str.contains(query_lower, na=False))
resultados_precios = medicamentos_df[mask].to_dict('records')
```

**2. El Diccionario Traductor (Paso Crítico):**
Para asegurar que la API de la FDA entienda la búsqueda, se usa un diccionario que mapea nombres en español a sus equivalentes en inglés. El método `.get()` se usa para evitar errores si un término no se encuentra.

```python
# app.py - Fragmento del uso del diccionario traductor
nombre_en_minusculas = nombre_para_api.lower()
# Si no encuentra la clave, usa el mismo nombre original.
nombre_busqueda_api = TRADUCTOR_PRINCIPIOS.get(nombre_en_minusculas, nombre_en_minusculas)
```

**3. Consulta a la API Externa y Traducción:**
Se realiza una petición a la API de la FDA y, si hay éxito, se traducen los resultados al español antes de enviarlos a la plantilla.

```python
# app.py - Fragmento de la llamada a la API y traducción
API_URL = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{nombre_busqueda_api}\"&limit=1"
response = requests.get(API_URL, timeout=10)
data = response.json()
# ... (lógica para procesar 'data')

translator = GoogleTranslator(source='en', target='es')
info_fda['description'] = translator.translate(info.get('description', [''])[0])
```

**4. Renderizado Final:**
La función `render_template` de Flask pasa todas las variables procesadas a la plantilla HTML para que sean mostradas al usuario.

```python
# app.py - Fragmento del renderizado
return render_template('index.html', 
                       medicamentos=resultados_precios, 
                       info_fda=info_fda,
                       query=query)
```

### 4.2. Interfaz de Usuario (`index.html` con Jinja2)

La interfaz es un único archivo HTML que cobra vida gracias al motor de plantillas Jinja2, que renderiza el contenido dinámicamente en el servidor.

**1. Renderizado Condicional de la Tabla de Precios:**
La tabla de resultados solo se muestra en la página si la variable `medicamentos` contiene datos. De lo contrario, no se genera nada de ese código HTML.

```html
<!-- index.html - Fragmento de renderizado condicional -->
{% if medicamentos %}
    <h2>Precios Encontrados</h2>
    <table>
        <thead>...</thead>
        <tbody>
            <!-- El bucle solo se ejecuta si hay medicamentos -->
        </tbody>
    </table>
{% elif query %}
    <p class="mensaje">No se encontraron precios para "{{ query }}".</p>
{% endif %}
```

**2. Bucle para Mostrar Resultados:**
Se utiliza un bucle `for` de Jinja2 para iterar sobre la lista `medicamentos` y crear una fila de tabla (`<tr>`) para cada resultado. Se aplica un filtro para formatear el precio a dos decimales.

```html
<!-- index.html - Fragmento del bucle de resultados -->
{% for med in medicamentos %}
<tr>
    <td>{{ med.Productos }}</td>
    <td>{{ med.PrincipioActivo }}</td>
    <td>S/ {{ "%.2f"|format(med.Precio|float) }}</td>
    <td>{{ med.Farmacias }}</td>
</tr>
{% endfor %}
```

**3. Visualización de Información de la FDA:**
De manera similar, la sección con la ficha técnica de la FDA solo se muestra si la variable `info_fda` contiene la información esperada.

```html
<!-- index.html - Fragmento de la info de la FDA -->
{% if info_fda.brand_name %}
    <div class="fda-info">
        <h2>Información de la FDA para: {{ info_fda.brand_name }}</h2>
        <p><strong>Nombre Genérico:</strong> {{ info_fda.generic_name }}</p>
        <h3>Descripción</h3>
        <p>{{ info_fda.description }}</p>
        ...
    </div>
{% endif %}
```

---

## 5. Despliegue y Acceso a la Aplicación

### 5.1. ¿Por qué Replit y no GitHub Pages?

*   **GitHub Pages** es una excelente plataforma para alojar **sitios web estáticos** (archivos HTML, CSS y JavaScript que se ejecutan en el navegador del cliente). Sin embargo, **no puede ejecutar código de backend como Python**. Nuestra aplicación depende críticamente de un servidor Flask para leer archivos, procesar búsquedas y comunicarse con APIs, por lo que GitHub Pages no era una opción viable.
*   **Replit**, en cambio, ofrece un **entorno de computación completo en la nube**. Proporciona un contenedor Linux que puede instalar las dependencias listadas en `requirements.txt` y ejecutar nuestro script `app.py`. Cuando Flask inicia el servidor, Replit detecta el puerto abierto y lo redirige automáticamente a una URL pública, haciendo que nuestra aplicación dinámica sea accesible para cualquiera.

### 5.2. Ejecución Local (Para Desarrolladores y Evaluadores)

Cualquier persona puede ejecutar una copia de esta aplicación en su propia computadora. Esto es ideal para probar, modificar o evaluar el código sin depender de una conexión a internet o de la plataforma Replit. Los pasos son los siguientes:

1.  **Descargar el Código:** Clonar o descargar el repositorio completo desde GitHub.
2.  **Instalar Dependencias:** Asegurarse de tener Python instalado y ejecutar `pip install -r requirements.txt` en la terminal para instalar Flask, Pandas y las demás librerías necesarias.
3.  **Ubicar los Datos:** Colocar el archivo `medicamentos_unificados.csv` dentro de la carpeta `data/`. **Este paso es crucial**, ya que la aplicación necesita este archivo para funcionar.
4.  **Ejecutar el Servidor:** Correr el comando `python app.py` en la terminal.
5.  **Acceder a la Aplicación:** Abrir un navegador web y visitar la dirección local `http://127.0.0.1:5001`. La aplicación será completamente funcional.