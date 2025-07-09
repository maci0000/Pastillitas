from flask import Flask, render_template, request
import pandas as pd
import requests
from deep_translator import GoogleTranslator

app = Flask(__name__)

TRADUCTOR_API = {
    'paracetamol': 'acetaminophen',
    'ibuprofeno': 'ibuprofen',
    'aspirina': 'aspirin',
    'amoxicilina': 'amoxicillin'
}

print("--- Iniciando aplicación Buscador de Medicamentos (Versión Final Profesional) ---")
try:
    df = pd.read_csv('medicamentos_unificados.csv', sep=';')
    df['Producto_lower'] = df['Producto'].astype(str).str.lower()
    df['PrincipioActivo_lower'] = df['PrincipioActivo'].astype(str).str.lower()
    print(" Base de datos local cargada correctamente.")
except FileNotFoundError:
    print("‼  ERROR: No se encontró 'medicamentos_unificados.csv'.")
    df = pd.DataFrame()

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('query', '').strip()
    resultados_locales = []
    resultados_api = []

    if not df.empty and query:
        search_query_lower = query.lower()

        mask = df['Producto_lower'].str.contains(search_query_lower, na=False) | \
               df['PrincipioActivo_lower'].str.contains(search_query_lower, na=False)
        
        df_resultados = df[mask]
        resultados_locales = df_resultados.to_dict('records')

    if query:
        search_query_lower = query.lower()

        query_para_api = search_query_lower
        
        if search_query_lower in TRADUCTOR_API:
            query_para_api = TRADUCTOR_API[search_query_lower]
            print(f"Traduciendo búsqueda para la API: '{search_query_lower}' -> '{query_para_api}'")
        
        print(f" Buscando '{query_para_api}' en la API de OpenFDA...")
        api_url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{query_para_api}"+OR+openfda.generic_name:"{query_para_api}"&limit=1'
        
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                resultados_api_raw = data.get('results', [])
                if resultados_api_raw:
                    print(" Traduciendo resultados de la API al español...")
                    translator = GoogleTranslator(source='en', target='es')
                    for info in resultados_api_raw:
                        if 'indications_and_usage' in info and info['indications_and_usage']:
                            texto_original = info['indications_and_usage'][0]
                            try: info['indications_and_usage_es'] = translator.translate(texto_original)
                            except Exception as e: info['indications_and_usage_es'] = f"{texto_original} (Error de traducción: {e})"
                        if 'openfda' in info and 'product_type' in info['openfda'] and info['openfda']['product_type']:
                            tipo = info['openfda']['product_type'][0]
                            info['product_type_es'] = 'Medicamento de Venta Libre' if tipo == 'HUMAN OTC DRUG' else 'Medicamento con Receta'
                resultados_api = resultados_api_raw
        except requests.exceptions.RequestException as e:
            print(f" Error de conexión con la API: {e}")

    return render_template(
        'index.html', 
        medicamentos=resultados_locales, 
        info_fda=resultados_api,
        query=query
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)