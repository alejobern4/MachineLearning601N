from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import re
import json
import pandas as pd
import numpy as np
import os
import joblib
import logging
from io import BytesIO
from werkzeug.utils import secure_filename
from . import linearRegression
from .regresionLogistica import regresion_logisitica, prediccion
from .conexionLocalBd import get_local_connection
from .conexionRenderBd import get_render_connection
from .convertidorImagenes import convertirImagen
from .randomForest import metricas


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

pd.set_option('io.excel.xlsx.reader', 'openpyxl')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 5 * 1024 * 1024
UPLOAD_FOLDER = 'temp_results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = joblib.load('cancer_model.pkl')

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def probar_conexion():
    try:
        conn = get_local_connection()
        print("Conexión exitosa")
    except Exception as e:
        print("Error al conectar con la base de datos:")
        print(e)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hello/<name>")
def hello_there(name):
    now = datetime.now()

    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! Hour: " + str(now)
    return content

@app.route("/casoUso")
def casoUso():
    return render_template("casoUso.html")


@app.route("/linearRegression", methods=["GET", "POST"])
def linear_regression():
    calculateResult = None
    plot_url = None
    
    if request.method == "POST":
        hours = float(request.form["hours"])
        calculateResult, plot_url = linearRegression.calculateGrade(hours)
    
    return render_template("linearRegression.html", result=calculateResult, plot_url=plot_url)

@app.route("/mapaRegresionLogistica")
def mapaRegresionLogistica():
    return render_template("mapaRegresionLogistica.html")


@app.route('/regresionLogistica', methods=['GET', 'POST'])
def regresionLogistica():
    prediction = None
    result, plot_url = regresion_logisitica()

    if request.method == 'POST':
        nivel = float(request.form['nivel'])
        frecuencia = float(request.form['frecuencia'])
        dispositivo = int(request.form['dispositivo'])
        prediction = prediccion(nivel, frecuencia, dispositivo)

    return render_template('regresionLogistica.html', result=result, prediction=prediction, plot_url=plot_url)

@app.route("/modelosClasificacion")
def mostrarModelos():
    conn = get_local_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT Id_Modelo, Nombre_Modelo FROM modelos_ml")
    modelos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("modelosClasificacion.html", modelos=modelos)

@app.route("/modelosClasificacion/<int:modelo_id>")
def detalle_modelo(modelo_id):
    conn = get_local_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Id_Modelo, Nombre_Modelo, Descripcion 
        FROM modelos_ml 
        WHERE Id_Modelo = %s
    """, (modelo_id,))
    modelo = cursor.fetchone()

    cursor.execute("""
        SELECT Id_Modelo, Nombre_Modelo, Descripcion 
        FROM modelos_ml
    """)
    modelos = cursor.fetchall()

    cursor.execute("""
        SELECT Id_Imagen, Nombre_Imagen, Imagen
        FROM imagenes 
        WHERE Id_Modelo = %s
    """, (modelo_id,))
    imagenes = cursor.fetchall()
    imagenes64 = convertirImagen(imagenes)

    cursor.execute("""
        SELECT Nombre_Link
        FROM fuentes_consulta 
        WHERE Id_Modelo = %s
    """, (modelo_id,))
    fuentes = cursor.fetchall()

    cursor.close()
    conn.close()

    if modelo:
        return render_template("detalleModelo.html", modelo=modelo, modelos=modelos, imagenes64=imagenes64, fuentes=fuentes)
    else:
        return "Modelo no encontrado", 404


@app.route('/randomForest')
def random_Forest():
    """Ruta principal que devuelve la página HTML"""
    return render_template('randomForest.html')

@app.route('/metrics')
def get_metrics():
    """Endpoint para obtener las métricas del modelo"""
    try:
        metrics, y_test = metricas()
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'test_samples': len(y_test)
        })
    
    except FileNotFoundError:
        return jsonify({'error': 'Archivo test_data.json no encontrado'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error al decodificar el archivo JSON'}), 400
    except Exception as e:
        app.logger.error(f"Error en endpoint /metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para procesar archivos Excel y hacer predicciones"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se subió ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    try:
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_FILE_SIZE:
            return jsonify({
                'error': f'El archivo es demasiado grande (límite: {MAX_FILE_SIZE/1024/1024:.1f}MB)'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Formato de archivo no válido. Solo se aceptan .xlsx o .xls'
            }), 400
        
        df = pd.read_excel(BytesIO(file.read()), engine='openpyxl')
        
        required_cols = ['radio', 'textura', 'simetria']
        df.columns = df.columns.str.lower().str.strip()
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                'error': f'Columnas faltantes: {", ".join(missing_cols)}',
                'columnas_recibidas': list(df.columns)
            }), 400
        
        for col in required_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return jsonify({
                    'error': f'La columna {col} contiene valores no numéricos'
                }), 400
        
        valid_ranges = {
            'radio': (0.1, 10.0),
            'textura': (0.1, 10.0),
            'simetria': (0.1, 10.0)
        }
        
        for col, (min_val, max_val) in valid_ranges.items():
            if df[col].min() < min_val or df[col].max() > max_val:
                return jsonify({
                    'error': f'Valores en {col} fuera del rango permitido ({min_val}-{max_val})'
                }), 400
        
        X = df[required_cols].values
        
        predictions = model.predict(X)
        
        try:
            probabilities = model.predict_proba(X)
            df['confianza'] = [f"{prob[pred]*100:.1f}%" for pred, prob in zip(predictions, probabilities)]
        except AttributeError:
            df['confianza'] = "N/A"
        
        df['prediccion'] = predictions
        df['resultado'] = df['prediccion'].apply(lambda x: 'Maligno' if x == 1 else 'Benigno')
        
        results_filename = secure_filename(f"resultados_{file.filename}")
        results_path = os.path.join(UPLOAD_FOLDER, results_filename)
        
        df.to_excel(results_path, index=False)
        
        return jsonify({
            'success': True,
            'data': df.to_dict('records'),
            'csv_data': df.to_csv(index=False),
            'excel_filename': results_filename
        })
    
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'El archivo Excel está vacío o corrupto'}), 400
    except Exception as e:
        app.logger.error(f"Error al procesar archivo: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Error al procesar el archivo: {str(e)}',
            'type': type(e).__name__
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Endpoint para descargar archivos de resultados"""
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
