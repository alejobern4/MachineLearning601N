import json
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import os

def cargaDatos():
    ruta1_json = "Datos/train_data.json"
    ruta1_json = os.path.join(os.path.dirname(__file__), "Datos/train_data.json")

    ruta2_json = "Datos/test_data.json"
    ruta2_json = os.path.join(os.path.dirname(__file__), "Datos/test_data.json")

    with open(ruta1_json, "r", encoding="utf-8") as file:
        data = json.load(file)
    df_train = pd.DataFrame(data)

    with open(ruta2_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        
    df_test = pd.DataFrame(data)
    df = pd.concat([df_train, df_test], ignore_index=True)
    return df

def regresion_logisitica():
    df = cargaDatos()

    # Variables
    X = df[['nivel', 'frecuencia_juego', 'dispositivo']]
    y = df['abandono']

    # Codificar variables categóricas
    X = pd.get_dummies(X, columns=['dispositivo'], drop_first=True)

    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Modelo
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Predicción y métricas
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    
    # Matriz de confusión
    conf_mat = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues')
    plt.title("Matriz de Confusion")
    plt.xlabel("Prediccion")
    plt.ylabel("Real")

    # Convertir a imagen
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Resultado
    result = {
        'accuracy': round(acc * 100, 2),
        'precision': round(prec * 100, 2),
        'recall': round(rec * 100, 2)
    }

    return result, plot_url

def prediccion(nivel, frecuencia_juego, dispositivo):
    df = cargaDatos()
    X = df[['nivel', 'frecuencia_juego', 'dispositivo']]

    # Escalar datos con los mismos parámetros
    scaler = StandardScaler()
    scaler.fit(X)

    X_input = np.array([[nivel, frecuencia_juego, dispositivo]])
    X_input_scaled = scaler.transform(X_input)

    model = LogisticRegression()
    model.fit(scaler.transform(X), df['abandono'])

    prediction = model.predict(X_input_scaled)[0]
    return prediction