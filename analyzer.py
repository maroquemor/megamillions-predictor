import sqlite3
from collections import Counter
import os

# Ruta dinámica para la base de datos (Render usa /tmp/)
NOMBRE_DB = '/tmp/megamillions.db' if os.environ.get('RENDER') else 'megamillions.db'

def analizar_frecuencias(limite=100):
    conn = sqlite3.connect(NOMBRE_DB)
    c = conn.cursor()
    c.execute('''
        SELECT white_1, white_2, white_3, white_4, white_5, megaball
        FROM draws ORDER BY draw_date DESC LIMIT ?
    ''', (limite,))
    filas = c.fetchall()
    conn.close()

    contador_blancas = Counter()
    contador_mega = Counter()
    for fila in filas:
        for i in range(5):
            contador_blancas[fila[i]] += 1
        contador_mega[fila[5]] += 1
    return contador_blancas, contador_mega

def sugerir_numeros():
    blancas_freq, mega_freq = analizar_frecuencias(limite=200)
    mas_comunes_blancas = [num for num, _ in blancas_freq.most_common(5)]
    mas_comunes_blancas.sort()
    megaball_sugerido = mega_freq.most_common(1)[0][0]
    return mas_comunes_blancas, megaball_sugerido

def obtener_calientes_frios():
    conn = sqlite3.connect(NOMBRE_DB)
    c = conn.cursor()
    c.execute('SELECT white_1, white_2, white_3, white_4, white_5, megaball FROM draws')
    filas = c.fetchall()
    conn.close()

    contador_blancas = Counter()
    contador_mega = Counter()
    for fila in filas:
        for i in range(5):
            contador_blancas[fila[i]] += 1
        contador_mega[fila[5]] += 1

    calientes_blancas = [num for num, _ in contador_blancas.most_common(10)]
    calientes_mega = [num for num, _ in contador_mega.most_common(5)]

    todos_blancas = set(range(1, 71))
    todos_mega = set(range(1, 26))
    aparecidos_blancas = set(contador_blancas.keys())
    aparecidos_mega = set(contador_mega.keys())

    frios_blancas = list(todos_blancas - aparecidos_blancas)
    frios_mega = list(todos_mega - aparecidos_mega)

    if not frios_blancas:
        frios_blancas = [num for num, _ in contador_blancas.most_common()[-10:]]
    if not frios_mega:
        frios_mega = [num for num, _ in contador_mega.most_common()[-5:]]

    return {
        'calientes_blancas': calientes_blancas,
        'calientes_mega': calientes_mega,
        'frios_blancas': frios_blancas[:10],
        'frios_mega': frios_mega[:5]
    }