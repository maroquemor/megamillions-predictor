from flask import Flask, render_template
import analyzer
import database
import sqlite3
import os

app = Flask(__name__)

# Inicializar la base de datos al arrancar
print("Inicializando base de datos...")
database.inicializar_base_datos()
print("Base de datos lista.")

@app.route('/')
def index():
    try:
        blancas, megaball = analyzer.sugerir_numeros()
        stats = analyzer.obtener_calientes_frios()

        conn = sqlite3.connect(database.NOMBRE_DB)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM draws')
        total = c.fetchone()[0]
        conn.close()

        return render_template('index.html',
                               blancas=blancas,
                               megaball=megaball,
                               stats=stats,
                               total=total)
    except Exception as e:
        return f"<h1>Error interno</h1><pre>{e}</pre>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)