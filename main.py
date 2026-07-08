from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import json

app = FastAPI()
DB_PATH = "/data/trading_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operaciones 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, volume REAL, 
                       entry_type INTEGER, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        # Usamos el parser nativo de FastAPI/Starlette en lugar del split manual,
        # que era frágil y podía romperse con JSON más complejo.
        data = await request.json()

        symbol = data.get('symbol')
        volume = data.get('volume')
        tipo   = data.get('type')  # 0 = BUY, 1 = SELL -- ESTE es el que va en entry_type

        if symbol is None or volume is None or tipo is None:
            return {"status": "error", "detail": "Faltan campos symbol/volume/type"}

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                       (symbol, volume, tipo, 'ABIERTA'))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, volume, entry_type FROM operaciones WHERE status = 'ABIERTA'")
    rows = cursor.fetchall()
    conn.close()

    # Construimos explícitamente el formato que espera el EA esclavo:
    # [id, symbol, volume, type, entry]
    # entry = 0 siempre aquí porque solo consultamos señales con status='ABIERTA' (abrir)
    senales = [[row[0], row[1], row[2], row[3], 0] for row in rows]

    return {"senales_activas": senales}


@app.get("/confirmar-ejecucion/{id_op}")
@app.post("/confirmar-ejecucion/{id_op}")
async def confirmar_ejecucion(id_op: int):
    # Marca la señal como ejecutada para que no se vuelva a enviar / abrir duplicada
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE operaciones SET status = 'EJECUTADA' WHERE id = ?", (id_op,))
    conn.commit()
    conn.close()
    return {"status": "ok", "id": id_op}


@app.get("/clear-signals")
async def limpiar():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operaciones")
    conn.commit()
    conn.close()
    return {"status": "limpio"}
