
from datetime import datetime

from flask import Flask, render_template,request,redirect
app = Flask(__name__)


usuarios = {}

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        password = request.form['password']
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
        nivel_cocina = request.form['nivel_cocina']

        if correo in usuarios:
            return render_template('registro.html', error="El correo ya está registrado.")
        
        usuarios[correo] = {
            'nombre': nombre,
            'apellidos': apellidos,
            'correo': correo,
            'password': password,
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
            'nivel_cocina': nivel_cocina
        }

        return redirect('/') 

    return render_template('registro.html')

@app.route('/')
def index():
    return render_template('index.html')

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
@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

if __name__ == '__main__':
    app.run(debug=True)
