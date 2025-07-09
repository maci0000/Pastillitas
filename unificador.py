import pandas as pd
import os

print("--- Iniciando Proceso de Unificación de Datos ---")


ruta_boticas = os.path.join('data', 'boticasysalud_raw_data.csv')
ruta_hogar = os.path.join('data', 'hogarysalud_raw_data.csv')

ruta_salida_unificada = 'medicamentos_unificados.csv'


try:
    print(f" Cargando archivo: {ruta_boticas}")
    df_boticas = pd.read_csv(ruta_boticas, sep=',', encoding='utf-8')
    df_boticas['Fuente'] = 'Boticas y Salud'
    print(" Archivo de Boticas y Salud cargado.")

    print(f" Cargando archivo: {ruta_hogar}")
    df_hogar = pd.read_csv(ruta_hogar, sep=';', encoding='utf-8-sig')
    df_hogar['Fuente'] = 'Hogar y Salud'
    print(" Archivo de Hogar y Salud cargado.")

    print("\n Uniendo los dos conjuntos de datos...")
    df_final = pd.concat([df_boticas, df_hogar], ignore_index=True)
    print(f"Total de productos antes de la limpieza: {len(df_final)}")

    print(" Realizando limpieza de datos...")

    df_final.dropna(subset=['Producto', 'Precio'], inplace=True)
    
    df_final['PrincipioActivo'].fillna('No especificado', inplace=True)
    
    df_final.drop_duplicates(inplace=True)
    
    print(f" Total de productos después de la limpieza: {len(df_final)}")

    df_final.to_csv(ruta_salida_unificada, index=False, sep=';', encoding='utf-8-sig')

    print("\n ¡Proceso completado!")
    print(f"Archivo final guardado en: '{ruta_salida_unificada}'")

except FileNotFoundError as e:
    print(f"\n ERROR: No se pudo encontrar un archivo.")
    print(f"Detalle: {e}")
    print("Asegúrate de que los scrapers hayan terminado y los archivos CSV existan en la carpeta 'data'.")
except Exception as e:
    print(f"\n Ocurrió un error inesperado: {e}")