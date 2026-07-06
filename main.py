from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import json
import os

app = FastAPI()

# Aseguramos que la DB se cree en el directorio actual
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
        data = json.loads(body)
        print(f"DEBUG: Datos recibidos para guardar: {data}") # Log para verificar
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                       (data.get('symbol'), data.get('volume'), data.get('entry'), 'ABIERTA'))
        conn.commit()
        conn.close()
        return {"status": "ok", "data_received": data}
    except Exception as e:
        print(f"DEBUG: Error en POST: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operaciones WHERE status = 'ABIERTA'")
    rows = cursor.fetchall()
    conn.close()
    return {"senales_activas": rows}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
