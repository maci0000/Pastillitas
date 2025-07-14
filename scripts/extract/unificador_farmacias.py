import pandas as pd
import os

# Rutas
path_boticas = "raw_data/boticas_salud.csv"
path_hogar = "raw_data/hogar_salud.csv"
output_path = "data/medicamentos_unificados.csv"

# Cargar los archivos
df_boticas = pd.read_csv(path_boticas)
df_hogar = pd.read_csv(path_hogar, on_bad_lines='skip')

# Renombrar columnas si fueran diferentes
df_boticas.rename(columns={
    "Producto": "Producto",
    "PrincipioActivo": "PrincipioActivo",
}, inplace=True)

df_hogar.rename(columns={
    "Producto": "Producto",
    "PrincipioActivo": "PrincipioActivo",
}, inplace=True)

# Verificar que ambas tengan la columna 'farmacia'
if "Farmacia" not in df_boticas.columns:
    df_boticas["Farmacia"] = "Boticas y Salud"
if "Farmacia" not in df_hogar.columns:
    df_hogar["Farmacia"] = "Hogar y Salud"

# Unir los DataFrames
df_final = pd.concat([df_boticas, df_hogar], ignore_index=True)

# Guardar CSV unificado
os.makedirs("data", exist_ok=True)
df_final.to_csv(output_path, index=False, encoding="utf-8")

print(f"✅ Archivo unificado guardado en: {output_path}")
