import sqlite3
from fastapi import FastAPI

app = FastAPI()
DB_PATH = "trading_data.db"

# Asegurar que la tabla siempre se cree al arrancar
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operaciones 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       symbol TEXT, 
                       volume REAL, 
                       entry_type INTEGER, 
                       status TEXT)''')
    conn.commit()
    conn.close()

# Ejecutar al iniciar la aplicación
init_db()

@app.get("/get-signals")
async def obtener_senales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, symbol, volume, entry_type FROM operaciones WHERE status = 'ABIERTA'")
        rows = cursor.fetchall()
        return {"senales_activas": rows}
    except sqlite3.OperationalError:
        return {"error": "Tabla no encontrada"}
    finally:
        conn.close()
