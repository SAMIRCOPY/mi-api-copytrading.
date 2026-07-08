from fastapi import FastAPI, Request
import sqlite3
import json

app = FastAPI()
DB_PATH = "trading_data.db"

# ... (mantén tu función init_db igual) ...

@app.post("/api/senal")
async def recibir_senal(request: Request):
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                   (data.get('symbol'), data.get('volume'), data.get('type'), 'ABIERTA'))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, volume, entry_type FROM operaciones WHERE status = 'ABIERTA'")
    rows = cursor.fetchall()
    conn.close()
    return {"senales_activas": rows}

# RUTA CORREGIDA: Esta debe coincidir exactamente con el esclavo
@app.post("/confirmar-ejecucion/{id}")
async def confirmar(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE operaciones SET status = 'PROCESADA' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "procesado"}

@app.get("/clear-signals")
async def limpiar():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operaciones")
    conn.commit()
    conn.close()
    return {"status": "limpio"}
