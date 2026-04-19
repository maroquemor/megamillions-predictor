import sqlite3
import csv
import os
import requests

# En Render, usar /tmp/ (escribible); en local usar carpeta actual
NOMBRE_DB = '/tmp/megamillions.db' if os.environ.get('RENDER') else 'megamillions.db'
URL_CSV = 'https://data.ny.gov/api/views/5xaw-6ayf/rows.csv?accessType=DOWNLOAD'
RUTA_CSV = '/tmp/megamillions_numbers.csv' if os.environ.get('RENDER') else 'data/megamillions_numbers.csv'

def descargar_csv():
    os.makedirs(os.path.dirname(RUTA_CSV), exist_ok=True)
    if not os.path.exists(RUTA_CSV):
        print(f"Descargando datos desde {URL_CSV}...")
        response = requests.get(URL_CSV)
        response.raise_for_status()
        with open(RUTA_CSV, 'wb') as f:
            f.write(response.content)
        print("Descarga completada.")
    else:
        print(f"Usando CSV existente en {RUTA_CSV}")

def crear_tablas():
    conn = sqlite3.connect(NOMBRE_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT UNIQUE NOT NULL,
            white_1 INTEGER,
            white_2 INTEGER,
            white_3 INTEGER,
            white_4 INTEGER,
            white_5 INTEGER,
            megaball INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def cargar_csv():
    conn = sqlite3.connect(NOMBRE_DB)
    c = conn.cursor()
    with open(RUTA_CSV, 'r', encoding='utf-8') as f:
        lector = csv.reader(f)
        next(lector)  # saltar encabezado
        for fila in lector:
            try:
                fecha = fila[0]
                # El formato del CSV de Data.gov es: "Draw Date", "Winning Numbers", "Mega Ball"
                # "Winning Numbers" viene como "10 22 35 48 61" (5 números separados por espacio)
                nums = fila[1].strip().split()
                if len(nums) != 5:
                    continue
                w1, w2, w3, w4, w5 = map(int, nums)
                megaball = int(fila[2])
                c.execute('''
                    INSERT OR IGNORE INTO draws
                    (draw_date, white_1, white_2, white_3, white_4, white_5, megaball)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (fecha, w1, w2, w3, w4, w5, megaball))
            except Exception as e:
                print(f"Error en fila: {e}")
    conn.commit()
    conn.close()
    print("Datos cargados en la base de datos.")

def inicializar_base_datos():
    descargar_csv()
    crear_tablas()
    cargar_csv()

if __name__ == '__main__':
    inicializar_base_datos()