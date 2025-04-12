from flask import Flask, render_template, request
from datetime import datetime
import re
from . import linearRegression
from .regresionLogistica import regresion_logisitica, prediccion
from .conexionLocalBd import get_local_connection
from .conexionRenderBd import get_render_connection
from .convertidorImagenes import convertirImagen

app = Flask(__name__)


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
