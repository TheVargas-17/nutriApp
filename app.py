from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'

API_BASE = "https://api.nal.usda.gov/fdc/v1"
API_KEY = "LbfNAj8Br4T9LIC7jz5YlLs3pfvDHEDHX4LEDBIO"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bsdnutri'


mysql = MySQL(app)

def crear_tablas():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            correo VARCHAR(150) UNIQUE NOT NULL,
            password TEXT,
            fecha_nacimiento DATE,
            sexo VARCHAR(20),
            peso FLOAT,
            altura FLOAT,
            actividad_fisica VARCHAR(50),
            objetivos VARCHAR(255),
            alergias TEXT,
            intolerancias TEXT,
            dietas TEXT,
            alimentos_no_gustan TEXT,
            experiencia_cocina VARCHAR(50),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_objetivos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            objetivo VARCHAR(150) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_alergias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            alergia VARCHAR(150) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_intolerancias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            intolerancia VARCHAR(150) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_dietas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            dieta VARCHAR(150) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')
    mysql.connection.commit()
    cursor.close()

def email_existe(correo):
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
    existe = cursor.fetchone() is not None
    cursor.close()
    return existe

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    alimento = request.form.get('nombre', '').strip()
    if not alimento:
        flash("Ingresa el nombre del alimento.", "error")
        return redirect(url_for('alimentos'))
    try:
        resp = requests.get(f"{API_BASE}/foods/search", params={"api_key": API_KEY, "query": alimento, "pageSize": 20})
        if resp.status_code == 200:
            data = resp.json()
            resultados = data.get("foods", [])
            return render_template("resultados.html", resultados=resultados, busqueda=alimento)
        flash("No se encontraron alimentos.", "error")
        return redirect(url_for('alimentos'))
    except Exception as e:
        print("ERROR buscar:", e)
        flash("Error al conectar con la API.", "error")
        return redirect(url_for('alimentos'))

@app.route('/food/<int:fdc_id>')
def food(fdc_id):
    try:
        resp = requests.get(f"{API_BASE}/foods/{fdc_id}", params={"api_key": API_KEY})
        if resp.status_code == 200:
            comida = resp.json()
            return render_template("food.html", comida=comida)
        flash("No se pudo obtener la información del alimento.", "error")
        return redirect(url_for('alimentos'))
    except Exception as e:
        print("ERROR food:", e)
        flash("Error al conectar con la API.", "error")
        return redirect(url_for('alimentos'))

@app.route('/alimentos')
def alimentos():
    return render_template('alimentos.html')

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        form = request.form
        correo = form['correo']

       
        if email_existe(correo):
            flash("El correo ya está registrado", "error")
            return render_template("registrar.html")

       
        registrar_usuario_db(form)
        flash("Registro exitoso, ahora puedes iniciar sesión", "success")
        return redirect(url_for("login"))

    
    return render_template("registro.html")


def registrar_usuario_db(form):
    cursor = mysql.connection.cursor(DictCursor)
    nombre = form['nombre']
    apellidos = form['apellidos']
    correo = form['correo']
    password = generate_password_hash(form['password'])
    fecha_nacimiento = form['fecha_nacimiento'] or None
    sexo = form['sexo']
    peso = float(form['peso']) if form['peso'] else None
    altura = float(form['altura']) if form['altura'] else None
    actividad_fisica = form['actividad_fisica']
    objetivos = form['objetivos']
    alimentos_no_gustan = form['alimentos_no_gustan']
    experiencia_cocina = form['experiencia_cocina']

    alergias = json.dumps(form.getlist('alergias'), ensure_ascii=False)
    intolerancias = json.dumps(form.getlist('intolerancias'), ensure_ascii=False)
    dietas = json.dumps(form.getlist('dietas'), ensure_ascii=False)

    query = """
        INSERT INTO usuarios
        (nombre, apellidos, correo, password, fecha_nacimiento, sexo, peso, altura, actividad_fisica,
         objetivos, alergias, intolerancias, dietas, alimentos_no_gustan, experiencia_cocina)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (nombre, apellidos, correo, password, fecha_nacimiento, sexo, peso, altura,
              actividad_fisica, objetivos, alergias, intolerancias, dietas,
              alimentos_no_gustan, experiencia_cocina)

    cursor.execute(query, values)
    mysql.connection.commit()
    cursor.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario:
            if check_password_hash(usuario["password"], password):

                session["usuario_id"] = usuario["id"]
                session["user_email"] = usuario["correo"]

                return redirect("/perfil")

            else:
                return "Contraseña incorrecta"

        else:
            return "Correo no encontrado"

    return render_template("login.html")



@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for('index'))



@app.route('/perfil')
def perfil():
    if "user_email" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (session["user_email"],))
    usuario = cursor.fetchone()
    cursor.close()

    usuario["alergias"] = json.loads(usuario["alergias"]) if usuario["alergias"] else []
    usuario["intolerancias"] = json.loads(usuario["intolerancias"]) if usuario["intolerancias"] else []
    usuario["dietas"] = json.loads(usuario["dietas"]) if usuario["dietas"] else []

    return render_template("perfil.html", usuario=usuario)





@app.route('/imc', methods=['GET', 'POST'])
def imc():
    resultado = None

    if request.method == 'POST':
        try:
            edad = int(request.form['edad'])
            sexo = request.form['sexo']
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])

            if altura == 0:
                raise ValueError("Altura no puede ser 0")

            imc = round(peso / (altura ** 2), 2)

            if imc < 18.5:
                mensaje = 'Bajo peso'
            elif imc < 25:
                mensaje = 'Normal'
            elif imc < 30:
                mensaje = 'Sobrepeso'
            else:
                mensaje = 'Obesidad'

            resultado = {
                'imc': imc,
                'mensaje': mensaje,
                'edad': edad,
                'sexo': sexo.capitalize()
            }

        except Exception as e:
            resultado = {'error': f'Error: {e}'}

    return render_template('imc.html', resultado=resultado)




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
        resultado = (22 if sexo == 'hombre' else 21) * (altura_m ** 2)
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

@app.route('/calrecetas', methods=['GET', 'POST'])
def calrecetas():
    resultados = []
    total = {"kcal": 0, "prote": 0, "carbs": 0, "grasas": 0}
    if request.method == 'POST':
        nombres = request.form.getlist('nombre')
        gramos_list = request.form.getlist('gramos')
        for i in range(len(nombres)):
            nombre = nombres[i]
            gramos = float(gramos_list[i]) if gramos_list[i] else 0
            busqueda = requests.get(f"{API_BASE}/foods/search", params={"api_key": API_KEY, "query": nombre, "pageSize": 1}).json()
            if not busqueda.get("foods"):
                continue
            fdc_id = busqueda["foods"][0]["fdcId"]
            detalle = requests.get(f"{API_BASE}/foods/{fdc_id}", params={"api_key": API_KEY}).json()
            kcal = prote = carbs = grasas = 0
            for n in detalle.get("foodNutrients", []):
                name = n.get("nutrientName","").lower()
                unit = n.get("unitName","")
                if "energy" in name and unit.lower() == "kcal":
                    kcal = n.get("value",0)
                elif "protein" in name:
                    prote = n.get("value",0)
                elif "carbohydrate" in name:
                    carbs = n.get("value",0)
                elif "fat" in name and "total" in name:
                    grasas = n.get("value",0)
            factor = gramos / 100
            datos = {
                "nombre": detalle.get("description",""),
                "gramos": gramos,
                "kcal": kcal * factor,
                "prote": prote * factor,
                "carbs": carbs * factor,
                "grasas": grasas * factor
            }
            resultados.append(datos)
            total["kcal"] += datos["kcal"]
            total["prote"] += datos["prote"]
            total["carbs"] += datos["carbs"]
            total["grasas"] += datos["grasas"]
    return render_template("calrecetas.html", resultados=resultados, total=total)

@app.route('/respuesta_correcta')
def respuesta_correcta():
    mensaje = "exacto my bro el pollo es el que tiene mas proteinas, eres todo un sabiondo ades ser amigo del Leonardo Vargas"
    return render_template('respuesta.html', mensaje=mensaje)

@app.route('/respuesta_incorrecta')
def respuesta_incorrecta():
    mensaje = "no le atinaste pa."
    return render_template('respuesta.html', mensaje=mensaje)

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/planes')
def planes():
    return render_template('planes.html')
if __name__ == '__main__':
    with app.app_context():
        crear_tablas()
    app.run(debug=True)

