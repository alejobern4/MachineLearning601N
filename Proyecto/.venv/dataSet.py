import pandas as pd
import json

archivo_excel = "archivo.xlsx"
hoja_deseada = "NombreDeLaHoja" 
archivo_json = "archivo_reestructurado.json"

df = pd.read_excel(archivo_excel, sheet_name=hoja_deseada)

data_list = df.to_dict(orient="records")

restructured_data = {
    "Study Hours": [item["Horas de estudio"] for item in data_list],
    "Final Grade": [item["Calificación (%)"] for item in data_list]
}

with open(archivo_json, "w", encoding="utf-8") as file:
    json.dump(restructured_data, file, indent=4)

print(f"Conversión completada. Datos guardados en '{archivo_json}'.")
