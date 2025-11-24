from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_mysqldb import MySQL
from workzeug.security import generate_pasword_hash
import re

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'

API_BASE = "https://api.nal.usda.gov/fdc/v1"
API_KEY = "LbfNAj8Br4T9LIC7jz5YlLs3pfvDHEDHX4LEDBIO"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_BD'] = 'prueba'

mysql = MySQL(app)

def create_tabla():
    try:
        cursor=mysql.connection.cursor()

@app.route('/buscar', methods=['POST'])
def buscar():
    fdc_id = request.form.get('fdc_id', '').strip()
    if not fdc_id.isdigit():
        flash("Debes ingresar un ID válido.", "error")
        return redirect(url_for('index'))
    return redirect(url_for('food', fdc_id=int(fdc_id)))

@app.route('/food/<int:fdc_id>')
def food(fdc_id):
    try:
        resp = requests.get(f"{API_BASE}/food/{fdc_id}",
                            params={"api_key": API_KEY})
        if resp.status_code == 200:
            comida = resp.json()
            return render_template("food.html", comida=comida)
        flash("No se encontró ese ID.", "error")
        return redirect(url_for('index'))
    except:
        flash("Error al conectar con la API.", "error")
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        fecha_nacimiento = request.form['fecha_nacimiento']
        sexo = request.form['sexo']
        peso = request.form['peso']
        altura = request.form['altura']
        actividad_fisica = request.form['actividad_fisica']
        objetivos = request.form['objetivos']
        alergias = request.form.getlist('alergias')
        intolerancias = request.form.getlist('intolerancias')
        dietas = request.form.getlist('dietas')
        alimentos_no_gustan = request.form['alimentos_no_gustan']
        experiencia_cocina = request.form['experiencia_cocina']

        session['usuario'] = {
            'nombre': nombre,
            'apellidos': apellidos,
            'correo': correo,
            'fecha_nacimiento': fecha_nacimiento,
            'sexo': sexo,
            'peso': peso,
            'altura': altura,
            'actividad_fisica': actividad_fisica,
            'objetivos': objetivos,
            'alergias': alergias,
            'intolerancias': intolerancias,
            'dietas': dietas,
            'alimentos_no_gustan': alimentos_no_gustan,
            'experiencia_cocina': experiencia_cocina
        }
        return redirect(url_for('perfil'))
    return render_template('registro.html')

@app.route('/perfil')
def perfil():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('registro'))
    return render_template('perfil.html', usuario=usuario)

@app.route('/planes')
def planes():
    return render_template('planes.html')

@app.route('/alimentos')
def alimentos():
    return render_template('alimentos.html')

@app.route('/imc')
def imc():
    return render_template('imc.html')

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

@app.route('/tmb', methods=['GET', 'POST'])
def tmb():
    resultado = None
    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        edad = float(request.form['edad'])
        sexo = request.form['sexo']
        if sexo == 'hombre':
            resultado = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * edad)
        else:
            resultado = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * edad)
    return render_template('tmb.html', resultado=resultado)

@app.route('/gasto-calorico', methods=['GET', 'POST'])
def gasto_calorico():
    resultado = None
    if request.method == 'POST':
        tmb_val = float(request.form['tmb'])
        factor = float(request.form['factor'])
        resultado = tmb_val * factor
    return render_template('gasto_calorico.html', resultado=resultado)

@app.route('/peso-ideal', methods=['GET', 'POST'])
def peso_ideal():
    resultado = None
    if request.method == 'POST':
        altura_m = float(request.form['altura']) / 100
        sexo = request.form['sexo']
        if sexo == 'hombre':
            resultado = 22 * (altura_m ** 2)
        else:
            resultado = 21 * (altura_m ** 2)
    return render_template('peso_ideal.html', resultado=resultado)

@app.route('/macros', methods=['GET', 'POST'])
def macros():
    resultado = None
    if request.method == 'POST':
        calorias = float(request.form['calorias'])
        prote = calorias * 0.30 / 4
        carbs = calorias * 0.40 / 4
        grasas = calorias * 0.30 / 9
        resultado = {
            'proteinas': round(prote, 1),
            'carbohidratos': round(carbs, 1),
            'grasas': round(grasas, 1)
        }
    return render_template('macros.html', resultado=resultado)

@app.route('/respuesta_correcta')
def respuesta_correcta():
    mensaje = "exacto my bro el pollo es el que tiene mas proteinas, eres todo un sabiondo ades ser amigo del Leonardo Vargas"
    return render_template('respuesta.html', mensaje=mensaje)

@app.route('/respuesta_incorrecta')
def respuesta_incorrecta():
    mensaje = "no le atinaste pa."
    return render_template('respuesta.html', mensaje=mensaje)

if __name__ == '__main__':
    app.run(debug=True)