from flask import Flask, render_template
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
