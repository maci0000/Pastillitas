#==============================================================================
# PASO 1: IMPORTACIÓN DE LIBRERIAS
#==============================================================================
# Flask es el micro-framework que me permite crear un servidor y la aplicación web
# Request me permite acceder a la informacion de la peticion del usuario
from flask import Flask, render_template, request
# Libreria fundamental, para la manipulacion de datos
import pandas as pd
import os
# Libreria para realizar HTP a otras páginas o APIs, como la de la FDA
import requests
# Libreria para traducri textos usando servicios como google translate.
from deep_translator import GoogleTranslator

# ==============================================================================
#  PASO 2 :EL DICCIONARIO 
# ==============================================================================

# Este diccionario es una pieza clave del proyecto.
# Su propósito es "traducir" los nombres comunes de principios activos en español
# a sus nombres técnicos o en inglés que utiliza la API de la FDA.

# Clave (izquierda): Nombre en español, en minúsculas y sin acentos para facilitar la búsqueda.
# Valor (derecha): Nombre correspondiente en inglés que entiende la API de la FDA.

TRADUCTOR_PRINCIPIOS = {
    # Analgésicos y Antiinflamatorios
    'paracetamol': 'acetaminophen',
    'ibuprofeno': 'ibuprofen',
    'diclofenaco': 'diclofenac',
    'ketoprofeno': 'ketoprofen',
    'naproxeno': 'naproxen',
    'meloxicam': 'meloxicam',
    'piroxicam': 'piroxicam',
    'celecoxib': 'celecoxib',
    'etoricoxib': 'etoricoxib',
    'aspirina': 'aspirin',
    'acido acetilsalicilico': 'aspirin',
    'ácido acetilsalicílico': 'aspirin',
    'tramadol': 'tramadol',
    'ketorolaco': 'ketorolac',
    'clonixinato de lisina': 'clonixin',
    'metamizol': 'metamizole',
    'dipirona': 'metamizole',
    'codeina': 'codeine',
    'morfina': 'morphine',
    
    # Antibióticos
    'amoxicilina': 'amoxicillin',
    'acido clavulanico': 'clavulanic acid',
    'ácido clavulánico': 'clavulanic acid',
    'ampicilina': 'ampicillin',
    'penicilina': 'penicillin',
    'azitromicina': 'azithromycin',
    'claritromicina': 'clarithromycin',
    'eritromicina': 'erythromycin',
    'ciprofloxacino': 'ciprofloxacin',
    'levofloxacino': 'levofloxacin',
    'moxifloxacino': 'moxifloxacin',
    'doxiciclina': 'doxycycline',
    'tetraciclina': 'tetracycline',
    'cefalexina': 'cephalexin',
    'cefuroxima': 'cefuroxime',
    'ceftriaxona': 'ceftriaxone',
    'cefixima': 'cefixime',
    'clindamicina': 'clindamycin',
    'metronidazol': 'metronidazole',
    'tinidazol': 'tinidazole',
    'sulfametoxazol': 'sulfamethoxazole',
    'trimetoprima': 'trimethoprim',
    'nitrofurantoina': 'nitrofurantoin',
    'gentamicina': 'gentamicin',
    'amikacina': 'amikacin',
    'vancomicina': 'vancomycin',
    'meropenem': 'meropenem',
    'imipenem': 'imipenem',
    'rifampicina': 'rifampin',
    
    # Antihistamínicos (Alergias)
    'loratadina': 'loratadine',
    'desloratadina': 'desloratadine',
    'cetirizina': 'cetirizine',
    'levocetirizina': 'levocetirizine',
    'fexofenadina': 'fexofenadine',
    'clorfenamina': 'chlorpheniramine',
    'difenhidramina': 'diphenhydramine',
    'hidroxicina': 'hydroxyzine',

    # Antihipertensivos (Presión Arterial)
    'losartan': 'losartan',
    'valsartan': 'valsartan',
    'irbesartan': 'irbesartan',
    'candesartan': 'candesartan',
    'enalapril': 'enalapril',
    'captopril': 'captopril',
    'lisinopril': 'lisinopril',
    'ramipril': 'ramipril',
    'amlodipino': 'amlodipine',
    'nifedipino': 'nifedipine',
    'felodipino': 'felodipine',
    'hidroclorotiazida': 'hydrochlorothiazide',
    'furosemida': 'furosemide',
    'espironolactona': 'spironolactone',
    'atenolol': 'atenolol',
    'metoprolol': 'metoprolol',
    'propranolol': 'propranolol',
    'carvedilol': 'carvedilol',
    'bisoprolol': 'bisoprolol',
    'doxazosina': 'doxazosin',
    'prazosina': 'prazosin',
    
    # Diabetes
    'metformina': 'metformin',
    'glibenclamida': 'glyburide',
    'gliclazida': 'gliclazide',
    'glimepirida': 'glimepiride',
    'sitagliptina': 'sitagliptin',
    'vildagliptina': 'vildagliptin',
    'saxagliptina': 'saxagliptin',
    'linagliptina': 'linagliptin',
    'dapagliflozina': 'dapagliflozin',
    'empagliflozina': 'empagliflozin',
    'canagliflozina': 'canagliflozin',
    'liraglutida': 'liraglutide',
    'insulina': 'insulin',

    # Colesterol y Triglicéridos
    'atorvastatina': 'atorvastatin',
    'rosuvastatina': 'rosuvastatin',
    'simvastatina': 'simvastatin',
    'pravastatina': 'pravastatin',
    'lovastatina': 'lovastatin',
    'fenofibrato': 'fenofibrate',
    'gemfibrozilo': 'gemfibrozil',
    'ezetimiba': 'ezetimibe',
    
    # Gastrointestinales
    'omeprazol': 'omeprazole',
    'esomeprazol': 'esomeprazole',
    'lansoprazol': 'lansoprazole',
    'pantoprazol': 'pantoprazole',
    'ranitidina': 'ranitidine',
    'famotidina': 'famotidine',
    'hidroxido de aluminio': 'aluminum hydroxide',
    'hidróxido de magnesio': 'magnesium hydroxide',
    'simeticona': 'simethicone',
    'loperamida': 'loperamide',
    'metoclopramida': 'metoclopramide',
    'domperidona': 'domperidone',
    'dimenhidrinato': 'dimenhydrinate',
    'bisacodilo': 'bisacodyl',
    'lactulosa': 'lactulose',
    'picosulfato de sodio': 'sodium picosulfate',
    'polietilenglicol': 'polyethylene glycol',
    
    # Respiratorios
    'salbutamol': 'albuterol',
    'salmeterol': 'salmeterol',
    'formoterol': 'formoterol',
    'bromuro de ipratropio': 'ipratropium bromide',
    'tiotropio': 'tiotropium',
    'budesonida': 'budesonide',
    'fluticasona': 'fluticasone',
    'beclometasona': 'beclomethasone',
    'mometasona': 'mometasone',
    'montelukast': 'montelukast',
    'ambroxol': 'ambroxol',
    'bromhexina': 'bromhexine',
    'dextrometorfano': 'dextromethorphan',
    'guaifenesina': 'guaifenesin',
    'codeina': 'codeine',
    
    # Sistema Nervioso Central (Ansiolíticos, Antidepresivos, etc.)
    'alprazolam': 'alprazolam',
    'clonazepam': 'clonazepam',
    'diazepam': 'diazepam',
    'lorazepam': 'lorazepam',
    'sertralina': 'sertraline',
    'fluoxetina': 'fluoxetine',
    'paroxetina': 'paroxetine',
    'escitalopram': 'escitalopram',
    'citalopram': 'citalopram',
    'venlafaxina': 'venlafaxine',
    'duloxetina': 'duloxetine',
    'amitriptilina': 'amitriptyline',

    # Antifúngicos (Hongos)
    'fluconazol': 'fluconazole',
    'itraconazol': 'itraconazole',
    'ketoconazol': 'ketoconazole',
    'terbinafina': 'terbinafine',
    'clotrimazol': 'clotrimazole',
    'miconazol': 'miconazole',
    'nistatina': 'nystatin',
    
    # Antivirales
    'aciclovir': 'acyclovir',
    'valaciclovir': 'valacyclovir',
    'oseltamivir': 'oseltamivir',
    
    # Vitaminas y Suplementos
    'acido folico': 'folic acid',
    'ácido fólico': 'folic acid',
    'hierro': 'iron',
    'calcio': 'calcium',
    'vitamina d': 'vitamin d',
    'vitamina c': 'ascorbic acid',
    'vitamina b12': 'cyanocobalamin',
    'complejo b': 'vitamin b complex',
    'magnesio': 'magnesium',
    'zinc': 'zinc',
    
    # Otros
    'levotiroxina': 'levothyroxine', # Tiroides
    'warfarina': 'warfarin', # Anticoagulante
    'clopidogrel': 'clopidogrel', # Antiagregante
    'sildenafilo': 'sildenafil', # Disfunción eréctil
    'tadalafilo': 'tadalafil',
    'finasterida': 'finasteride', # Próstata / Cabello
    'tamsulosina': 'tamsulosin', # Próstata
    'prednisona': 'prednisone', # Corticoide
    'dexametasona': 'dexamethasone',
    'hidrocortisona': 'hydrocortisone',
    'metilprednisolona': 'methylprednisolone',
    'acido ursodesoxicolico': 'ursodiol', # Hígado
    'allopurinol': 'allopurinol' # Gota
}

# ==============================================================================
#  PASO 3 :CONFIGURACIÓN DE FLASK
# ==============================================================================

# Se crea la instancia principal de la aplicación Flask.
# template_folder: Le indica a Flask dónde buscar los archivos HTML (plantillas).
# static_folder: Le indica a Flask dónde buscar los archivos estáticos (CSS, JavaScript, imágenes).

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# ==============================================================================
#  PASO 4 : RUTA AL ARCHIVO DE DATOS (CSV)
# ==============================================================================

# Se define la ruta base del proyecto para que funcione en cualquier sistema operativo.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Se construye la ruta completa y segura hacia el archivo CSV que contiene los precios de los medicamentos.
CSV_FILE = os.path.join(BASE_DIR, 'data', 'medicamentos_unificados.csv')
# Se inicializa una variable global para almacenar los datos del CSV. Se empieza como None.
medicamentos_df = None

def cargar_medicamentos():
    """Carga el CSV de medicamentos al iniciar la app."""
    global medicamentos_df # usamos eso para poder modificar la variable definida fuera de la función.
    try:
        medicamentos_df = pd.read_csv(CSV_FILE)                               # intenta leer el CSV y lo garga a dataframe
        # se asegura qeu las columnas de busqueda sean de tipo string para evitar errores
        medicamentos_df['Productos'] = medicamentos_df['Productos'].astype(str)
        medicamentos_df['PrincipioActivo'] = medicamentos_df['PrincipioActivo'].astype(str)
        print(f" CSV '{CSV_FILE}' cargado.")
    except Exception as e:
        # Si ocurre cualquier error al leer el archivo (ej. no existe, está corrupto)
        # se imprime una advertencia y se crea un DataFrame vacío para que la app no se caiga.
        print(f" ADVERTENCIA: No se pudo cargar '{CSV_FILE}'. La búsqueda de precios no funcionará. Error: {e}")
        medicamentos_df = pd.DataFrame()

# ==============================================================================
#  PASO 5 : RUTA PRINCIPAL QUE MANEJA LA LOGICA DE LA BUSQUEDA
# ==============================================================================

@app.route('/', methods=['GET'])
def index_y_busqueda():
    """
    Esta única función maneja tanto la página inicial como los resultados de búsqueda. Y PROCESA UNA BUSQUEDA
    DE ENCONTRAR PRECIOS Y OBTENER INFORMACION DE LA DFA CUANDO EL USUARIO ENVIA EL FORMULARIO
    """
    #obtiene el termino de busqueda de la URL
    # y el .strip() eliman los espacios en blanco de inicio a fin.
    query = request.args.get('query', '').strip()

    # iniciamos las variables que iran al index
    resultados_precios = []                        # lista para medicamentos encontrados en el CSV
    info_fda = {}                                  # Diccionario para informacion del API del FDA

# ==============================================================================
#  PASO 6 : Logica de busqueda de precios
# ==============================================================================

     # Solo se ejecuta si el usuario ha escrito algo en la barra de búsqueda (`query`)
     # y si los datos del CSV se cargaron correctamente (`not medicamentos_df.empty`).
    if query and not medicamentos_df.empty:
        query_lower = query.lower()
        
        # Creamos una "máscara" de búsqueda en pandas. Esto es muy eficiente.
        # Busca la `query_lower` en la columna 'Productos' O en la columna 'PrincipioActivo'.
        # `na=False` evita errores si hay celdas vacías en el CSV.
        mask = (medicamentos_df['Productos'].str.lower().str.contains(query_lower, na=False)) | \
               (medicamentos_df['PrincipioActivo'].str.lower().str.contains(query_lower, na=False))
        resultados_precios = medicamentos_df[mask].to_dict('records')

        # COMO EL CONSULTAMOS AL API DE LA FDA
        # Si se encontraron resultados de precios en nuestro CSV, procedemos a buscar info en la FDA.
        if resultados_precios:
            # Tomamos el primer medicamento de la lista para obtener su principio activo.
            # Esta es una simplificación: asumimos que todos los resultados de la búsqueda
            # comparten el mismo principio activo principal.
            primer_resultado = resultados_precios[0]
            principio_activo = primer_resultado.get('PrincipioActivo', 'No encontrado')

            # Preparamos el término que se usará para consultar la API de la FDA.
            # Se extrae la primera palabra del principio activo o del nombre del producto.
            # Esto se hace para tener un nombre más "limpio" y genérico.
            nombre_para_api = ''
            if principio_activo and principio_activo.lower() != 'no encontrado':
                # Si hay un principio activo, usamos su primera palabra.
                nombre_para_api = principio_activo.split(' ')[0].strip().replace(',', '')
            else:
                # Si no, usamos la primera palabra del nombre del producto.
                nombre_para_api = primer_resultado.get('Productos', '').split(' ')[0].strip().replace(',', '')
            
# ==============================================================================
#  PASO 7 : USAR EL DICCIONARIO ANTES DE USAR EL API
# ==============================================================================

            if nombre_para_api:
                # Convertimos a minúsculas para buscar en el diccionario
                nombre_en_minusculas = nombre_para_api.lower()
                
                # Buscamos en el diccionario. El método .get() es seguro:
                # - Si encuentra la clave (ej. 'paracetamol'), devuelve su valor ('acetaminophen').
                # - Si NO la encuentra, devuelve el valor por defecto, que hemos puesto que sea el mismo
                #   nombre original (`nombre_en_minusculas`). Esto evita que la app se caiga.
                nombre_busqueda_api = TRADUCTOR_PRINCIPIOS.get(nombre_en_minusculas, nombre_en_minusculas)

                # Construimos la URL para la petición a la API de la FDA.
                # `limit=1` para obtener solo el resultado más relevante.
                API_URL = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{nombre_busqueda_api}\"&limit=1"
                print(f" Consultando API de FDA con el término: '{nombre_busqueda_api}'...")
                
                try:
                    response = requests.get(API_URL, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Verificamos si la respuesta contiene la sección 'results'.
                    if 'results' in data and len(data['results']) > 0:
                        info = data['results'][0]
                        print(" Información encontrada en FDA. Procediendo a traducir...")

                        #  Inicio del bloque de traducción 
                        try:
                            translator = GoogleTranslator(source='en', target='es')
                            
                            # Creamos una función auxiliar para no repetir código.
                            # Traduce un texto si es válido; si no, devuelve "No disponible".
                            def traducir_texto(texto_original):
                                if texto_original and isinstance(texto_original, str) and texto_original.strip() != '':
                                    return translator.translate(texto_original)
                                return "No disponible"
                            
                            # Llenamos el diccionario `info_fda` con los datos extraídos y traducidos.
                            info_fda = {
                                'brand_name': info.get('openfda', {}).get('brand_name', ['N/A'])[0],
                                'generic_name': info.get('openfda', {}).get('generic_name', ['N/A'])[0],
                                'description': traducir_texto(info.get('description', [''])[0]),
                                'indications_and_usage': traducir_texto(info.get('indications_and_usage', [''])[0]),
                                'warnings': traducir_texto(info.get('warnings', [''])[0])
                            }
                            print(" Traducción completada.")

                        except Exception as e_translate:
                            # Si falla la traducción (ej. API de Google no responde), mostramos los datos en inglés.
                            print(f" Error durante la traducción: {e_translate}. Se mostrará el texto en inglés.")
                            info_fda = {
                                'brand_name': info.get('openfda', {}).get('brand_name', ['N/A'])[0],
                                'generic_name': info.get('openfda', {}).get('generic_name', ['N/A'])[0],
                                'description': info.get('description', ['No description available.'])[0] + " (Traducción no disponible)",
                                'indications_and_usage': info.get('indications_and_usage', ['No indications and usage information available.'])[0] + " (Traducción no disponible)",
                                'warnings': info.get('warnings', ['No warnings information available.'])[0] + " (Traducción no disponible)"
                            }
                        #  Fin del bloque de traducción 

                    else:
                        # Si la API de la FDA no encontró resultados para ese medicamento.
                        info_fda['message'] = f'No se encontró información para "{nombre_busqueda_api}" en la base de datos de la FDA.'
                        print(f" No se encontró información en FDA.")

                except requests.exceptions.RequestException as e:
                    # Si hubo un error de red (ej. no hay internet, la API de la FDA está caída).
                    print(f" Error de red al contactar FDA: {e}")
                    info_fda['error'] = 'No se pudo conectar con la API de la FDA.'
                
# ==============================================================================
#   FIN DE LA LÓGICA DE BÚSQUEDA EN API
# ==============================================================================
   
    # Finalmente, renderizamos la plantilla HTML 'index.html'.
    # Le pasamos todas las variables que hemos preparado:
    # - medicamentos: La lista de precios encontrados.
    # - info_fda: La información de la FDA (traducida o no).
    # - query: El término que el usuario buscó (para mostrarlo de nuevo en la barra de búsqueda).
    return render_template('index.html', 
                           medicamentos=resultados_precios, 
                           info_fda=info_fda,
                           query=query)

# eNTRA LA APP
if __name__ == '__main__':
    # 1. Carga los datos del CSV en memoria antes de que el servidor acepte peticiones.
    cargar_medicamentos()
    # 2. Inicia el servidor de desarrollo de Flask.
    #    debug=True: Activa el modo de depuración, que recarga el servidor con cada cambio y muestra errores detallados.
    #    host='0.0.0.0': Hace que el servidor sea accesible desde cualquier dispositivo en la misma red.
    #    port=5001: Define el puerto en el que correrá la aplicación.
    app.run(debug=True, host='0.0.0.0', port=5001)