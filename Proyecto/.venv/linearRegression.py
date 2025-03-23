import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import json
import os
import matplotlib.pyplot as plt
import base64
import io

#Data Linear Regression
ruta_json = "../archivo_reestructurado.json"

ruta_json = os.path.join(os.path.dirname(__file__), "../archivo_reestructurado.json")

with open(ruta_json, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)

x = df[["Horas de estudio"]]
y = df[["Calificacion"]]
 
model = LinearRegression()
model.fit(x, y)
def calculateGrade(hours):
    result = model.predict([[hours]])[0][0]

    x_range = np.linspace(min(x["Horas de estudio"]), max(x["Horas de estudio"]), 100).reshape(-1, 1)
    y_pred = model.predict(x_range)

    plt.figure()
    plt.scatter(df["Horas de estudio"], df["Calificacion"], color='blue', label='Datos reales')
    plt.plot(x_range, y_pred, color='red', linewidth=2, label='Regresión Lineal')
    plt.xlabel("Horas de estudio")
    plt.ylabel("Calificacion %")
    plt.title("Regresión Lineal")
    plt.legend()
    plt.grid()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return result, plot_url
