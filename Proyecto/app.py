from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re
import linearRegression
from regresionLogistica import regresion_logisitica, prediccion

app = Flask(__name__)

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

@app.route("/MapaRegresionLogistica")
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

