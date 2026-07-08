from fastapi import FastAPI, Request
import sqlite3
import json

app = FastAPI()
DB_PATH = "trading_data.db"

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
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                       (data.get('symbol'), data.get('volume'), data.get('type'), 'ABIERTA'))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": "Error al procesar JSON"}

@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, volume, entry_type FROM operaciones WHERE status = 'ABIERTA' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return {"senales_activas": [list(row)] if row else []}

@app.post("/confirmar-ejecucion/{id}")
async def confirmar(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE operaciones SET status = 'PROCESADA' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "procesado"}
