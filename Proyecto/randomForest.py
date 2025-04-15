import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, f1_score
import joblib 
import os

ruta1_json = "Datos/train_data_cancer.json"
ruta1_json = os.path.join(os.path.dirname(__file__), "Datos/train_data_cancer.json")

ruta2_json = "Datos/test_data_cancer.json"
ruta2_json = os.path.join(os.path.dirname(__file__), "Datos/test_data_cancer.json")

with open(ruta1_json, "r", encoding="utf-8") as file:
    train_data = json.load(file)

with open(ruta2_json, "r", encoding="utf-8") as file:
    test_data = json.load(file)

X_train = np.array([[d['radio'], d['textura'], d['simetria']] for d in train_data])
y_train = np.array([d['clase'] for d in train_data])
X_test = np.array([[d['radio'], d['textura'], d['simetria']] for d in test_data])
y_test = np.array([d['clase'] for d in test_data])

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(f"Precision: {precision_score(y_test, y_pred)}")
print(f"Recall: {recall_score(y_test, y_pred)}")
print("Matriz de confusión:")
print(confusion_matrix(y_test, y_pred))

joblib.dump(model, 'cancer_model.pkl')

def metricas():
    ruta2_json = "Datos/test_data_cancer.json"
    ruta2_json = os.path.join(os.path.dirname(__file__), "Datos/test_data_cancer.json")
    with open(ruta2_json, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    X_test = np.array([[d['radio'], d['textura'], d['simetria']] for d in test_data])
    y_test = np.array([d['clase'] for d in test_data])
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred) *100,
        'precision': precision_score(y_test, y_pred) *100,
        'recall': recall_score(y_test, y_pred) *100,
        'f1_score': f1_score(y_test, y_pred) *100,
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
    }

    return metrics, y_test