from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'

API_BASE = "https://api.nal.usda.gov/fdc/v1"
API_KEY = "LbfNAj8Br4T9LIC7jz5YlLs3pfvDHEDHX4LEDBIO"


@app.route('/buscar', methods=['POST'])
def buscar():
    alimento = request.form.get('nombre', '').strip()

    if not alimento:
        flash("Ingresa el nombre del alimento.", "error")
        return redirect(url_for('alimentos'))

    try:
        resp = requests.get(
            f"{API_BASE}/foods/search",
            params={"api_key": API_KEY, "query": alimento, "pageSize": 20}
        )

        if resp.status_code == 200:
            data = resp.json()
            resultados = data.get("foods", [])

            return render_template(
                "resultados.html",
                resultados=resultados,
                busqueda=alimento
            )

        flash("No se encontraron alimentos.", "error")
        return redirect(url_for('alimentos'))

    except Exception as e:
        print("ERROR:", e)
        flash("Error al conectar con la API.", "error")
        return redirect(url_for('alimentos'))


@app.route('/food/<int:fdc_id>')
def food(fdc_id):
    try:
        resp = requests.get(
            f"{API_BASE}/foods/{fdc_id}",
            params={"api_key": API_KEY}
        )

        if resp.status_code == 200:
            comida = resp.json()
            return render_template("food.html", comida=comida)

        flash("No se pudo obtener la información del alimento.", "error")
        return redirect(url_for('alimentos'))

    except Exception as e:
        print("ERROR:", e)
        flash("Error al conectar con la API.", "error")
        return redirect(url_for('alimentos'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        session['usuario'] = {
            key: request.form.get(key)
            for key in [
                'nombre', 'apellidos', 'correo', 'fecha_nacimiento', 'sexo',
                'peso', 'altura', 'actividad_fisica', 'objetivos',
                'alimentos_no_gustan', 'experiencia_cocina'
            ]
        }
        session['usuario']['alergias'] = request.form.getlist('alergias')
        session['usuario']['intolerancias'] = request.form.getlist('intolerancias')
        session['usuario']['dietas'] = request.form.getlist('dietas')

        return redirect(url_for('perfil'))

    return render_template('registro.html')


@app.route('/perfil')
def perfil():
    if not session.get('usuario'):
        return redirect(url_for('registro'))
    return render_template('perfil.html', usuario=session['usuario'])


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
    if request.method == 'POST':   # ← CORREGIDO
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
        resultado = (22 if sexo == 'hombre' else 21) * (altura_m ** 2)
    return render_template('peso_ideal.html', resultado=resultado)


@app.route('/macros', methods=['GET', 'POST'])
def macros():
    resultado = None
    if request.method == 'POST':   # ← CORREGIDO
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


# --------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
