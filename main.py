from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import json

app = FastAPI()

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect("trading_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operaciones 
                      (id INTEGER PRIMARY KEY, symbol TEXT, volume REAL, 
                       entry_type INTEGER, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        body = await request.body()
        data = json.loads(body)
        conn = sqlite3.connect("trading_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                       (data.get('symbol'), data.get('volume'), data.get('entry'), 'ABIERTA'))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Solución para el error 404: Definir el endpoint que faltaba
@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect("trading_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operaciones WHERE status = 'ABIERTA'")
    rows = cursor.fetchall()
    conn.close()
    return {"senales_activas": rows}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
