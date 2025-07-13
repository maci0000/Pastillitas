# app.py (en la raíz del proyecto, versión SIN JAVASCRIPT y CON DICCIONARIO)

from flask import Flask, render_template, request
import pandas as pd
import os
import requests
from deep_translator import GoogleTranslator

# ==============================================================================
#  PASO 1:EL DICCIONARIO 
# ==============================================================================
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
#  FIN DEL DICCIONARIO
# ==============================================================================


# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# --- RUTA AL ARCHIVO DE DATOS (CSV) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'medicamentos_unificados.csv')
medicamentos_df = None

def cargar_medicamentos():
    """Carga el CSV de medicamentos al iniciar la app."""
    global medicamentos_df
    try:
        medicamentos_df = pd.read_csv(CSV_FILE)
        medicamentos_df['Productos'] = medicamentos_df['Productos'].astype(str)
        medicamentos_df['PrincipioActivo'] = medicamentos_df['PrincipioActivo'].astype(str)
        print(f"✅ CSV '{CSV_FILE}' cargado.")
    except Exception as e:
        print(f"❌ ADVERTENCIA: No se pudo cargar '{CSV_FILE}'. La búsqueda de precios no funcionará. Error: {e}")
        medicamentos_df = pd.DataFrame()

# --- RUTA PRINCIPAL QUE MANEJA TODO ---

@app.route('/', methods=['GET'])
def index_y_busqueda():
    """
    Esta única función maneja tanto la página inicial como los resultados de búsqueda.
    """
    query = request.args.get('query', '').strip()
    
    resultados_precios = []
    info_fda = {}

    if query and not medicamentos_df.empty:
        query_lower = query.lower()
        
        mask = (medicamentos_df['Productos'].str.lower().str.contains(query_lower, na=False)) | \
               (medicamentos_df['PrincipioActivo'].str.lower().str.contains(query_lower, na=False))
        resultados_precios = medicamentos_df[mask].to_dict('records')

        if resultados_precios:
            primer_resultado = resultados_precios[0]
            principio_activo = primer_resultado.get('PrincipioActivo', 'No encontrado')

            nombre_para_api = ''
            if principio_activo and principio_activo.lower() != 'no encontrado':
                nombre_para_api = principio_activo.split(' ')[0].strip().replace(',', '')
            else:
                nombre_para_api = primer_resultado.get('Productos', '').split(' ')[0].strip().replace(',', '')
            
            # ==============================================================================
            #  PASO 2: USAR EL DICCIONARIO ANTES DE LLAMAR A LA API
            # ==============================================================================
            if nombre_para_api:
                # Convertimos a minúsculas para buscar en el diccionario
                nombre_en_minusculas = nombre_para_api.lower()
                
                # Buscamos en el diccionario. Si no lo encuentra, usa el mismo nombre original.
                nombre_busqueda_api = TRADUCTOR_PRINCIPIOS.get(nombre_en_minusculas, nombre_en_minusculas)

                API_URL = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{nombre_busqueda_api}\"&limit=1"
                print(f"🔍 Consultando API de FDA con el término: '{nombre_busqueda_api}'...")
                
                try:
                    response = requests.get(API_URL, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'results' in data and len(data['results']) > 0:
                        info = data['results'][0]
                        print("✅ Información encontrada en FDA. Procediendo a traducir...")

                        # ---- Inicio del bloque de traducción ----
                        try:
                            translator = GoogleTranslator(source='en', target='es')

                            def traducir_texto(texto_original):
                                if texto_original and isinstance(texto_original, str) and texto_original.strip() != '':
                                    return translator.translate(texto_original)
                                return "No disponible"

                            info_fda = {
                                'brand_name': info.get('openfda', {}).get('brand_name', ['N/A'])[0],
                                'generic_name': info.get('openfda', {}).get('generic_name', ['N/A'])[0],
                                'description': traducir_texto(info.get('description', [''])[0]),
                                'indications_and_usage': traducir_texto(info.get('indications_and_usage', [''])[0]),
                                'warnings': traducir_texto(info.get('warnings', [''])[0])
                            }
                            print("✅ Traducción completada.")

                        except Exception as e_translate:
                            print(f"⚠️ Error durante la traducción: {e_translate}. Se mostrará el texto en inglés.")
                            info_fda = {
                                'brand_name': info.get('openfda', {}).get('brand_name', ['N/A'])[0],
                                'generic_name': info.get('openfda', {}).get('generic_name', ['N/A'])[0],
                                'description': info.get('description', ['No description available.'])[0] + " (Traducción no disponible)",
                                'indications_and_usage': info.get('indications_and_usage', ['No indications and usage information available.'])[0] + " (Traducción no disponible)",
                                'warnings': info.get('warnings', ['No warnings information available.'])[0] + " (Traducción no disponible)"
                            }
                        # ---- Fin del bloque de traducción ----

                    else:
                        info_fda['message'] = f'No se encontró información para "{nombre_busqueda_api}" en la base de datos de la FDA.'
                        print(f"🤷 No se encontró información en FDA.")

                except requests.exceptions.RequestException as e:
                    print(f"❌ Error de red al contactar FDA: {e}")
                    info_fda['error'] = 'No se pudo conectar con la API de la FDA.'
                
            # ==============================================================================
            #  FIN DE LA LÓGICA DE BÚSQUEDA EN API
            # ==============================================================================

    return render_template('index.html', 
                           medicamentos=resultados_precios, 
                           info_fda=info_fda,
                           query=query)

# --- INICIALIZACIÓN ---
if __name__ == '__main__':
    cargar_medicamentos()
    app.run(debug=True, host='0.0.0.0', port=5001)