from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'  


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

@app.route('/cal')
def calculadoras():
    return render_template('calculadoras.html')

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')


@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

if __name__ == '__main__':
    app.run(debug=True)
