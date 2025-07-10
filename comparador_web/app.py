from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Cargar el CSV una sola vez al iniciar la aplicación
CSV_FILE = 'medicamentos_unificados.csv'
medicamentos_df = None

def cargar_medicamentos():
    """Carga el archivo CSV de medicamentos"""
    global medicamentos_df
    try:
        if os.path.exists(CSV_FILE):
            medicamentos_df = pd.read_csv(CSV_FILE)
            print(f"✅ CSV cargado exitosamente: {len(medicamentos_df)} registros")
        else:
            print(f"❌ No se encontró el archivo: {CSV_FILE}")
            medicamentos_df = pd.DataFrame()  # DataFrame vacío
    except Exception as e:
        print(f"❌ Error al cargar CSV: {e}")
        medicamentos_df = pd.DataFrame()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/buscar')
def buscar_medicamentos():
    """Endpoint para buscar medicamentos"""
    nombre = request.args.get('nombre', '').strip()
    
    if not nombre:
        return jsonify({
            'error': 'Debe proporcionar un nombre para buscar',
            'resultados': []
        }), 400
    
    if medicamentos_df is None or medicamentos_df.empty:
        return jsonify({
            'error': 'No se pudo cargar la base de datos de medicamentos',
            'resultados': []
        }), 500
    
    try:
        # Buscar medicamentos que contengan el nombre (sin distinguir mayúsculas/minúsculas)
        # Asumiendo que la columna se llama 'nombre' - ajusta según tu CSV
        resultados = medicamentos_df[
            medicamentos_df['nombre'].str.contains(nombre, case=False, na=False)
        ]
        
        # Convertir a diccionario para JSON
        medicamentos_encontrados = resultados.to_dict('records')
        
        return jsonify({
            'total': len(medicamentos_encontrados),
            'busqueda': nombre,
            'resultados': medicamentos_encontrados
        })
        
    except KeyError:
        return jsonify({
            'error': 'La columna "nombre" no existe en el CSV. Verifica la estructura del archivo.',
            'resultados': []
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Error en la búsqueda: {str(e)}',
            'resultados': []
        }), 500

@app.route('/info')
def info():
    """Endpoint para obtener información sobre la base de datos"""
    if medicamentos_df is None or medicamentos_df.empty:
        return jsonify({
            'estado': 'error',
            'mensaje': 'Base de datos no disponible'
        })
    
    return jsonify({
        'estado': 'ok',
        'total_medicamentos': len(medicamentos_df),
        'columnas': list(medicamentos_df.columns)
    })

if __name__ == '__main__':
    # Cargar medicamentos al iniciar
    cargar_medicamentos()
    
    # Iniciar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)