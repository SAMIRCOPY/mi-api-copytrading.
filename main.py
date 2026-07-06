from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import json
import os

app = FastAPI()
DB_PATH = "trading_data.db"

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operaciones 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, volume REAL, 
                       entry_type INTEGER, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Ruta para recibir señales (POST)
@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        body = await request.body()
        body_str = body.decode('utf-8').strip()
        
        # Limpieza para extraer solo el primer objeto JSON válido
        json_str = body_str.split('}')[0] + '}'
        data = json.loads(json_str)
        
        print(f"Datos procesados correctamente: {data}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                       (data.get('symbol'), data.get('volume'), data.get('entry'), 'ABIERTA'))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        print(f"Error procesando: {e}")
        return {"status": "error"}

# Ruta para consultar señales (GET)
@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM operaciones WHERE status = 'ABIERTA'")
        rows = cursor.fetchall()
        return {"senales_activas": rows}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

# Ruta para limpiar la base de datos (GET)
@app.get("/clear-signals")
async def limpiar_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM operaciones")
        conn.commit()
        return {"status": "Base de datos limpiada correctamente"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
