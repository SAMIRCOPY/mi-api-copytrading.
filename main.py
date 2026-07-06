from fastapi import FastAPI, Request
import sqlite3
import uvicorn

app = FastAPI()

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect("trading_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operaciones 
                      (id INTEGER PRIMARY KEY, symbol TEXT, volume REAL, 
                       entry_type INTEGER, status TEXT, profit REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.post("/api/senal")
async def recibir_senal(request: Request):
    data = await request.json()
    
    conn = sqlite3.connect("trading_data.db")
    cursor = conn.cursor()
    
    # Si entry=0 es apertura, si entry=1 es cierre
    if data['entry'] == 0:
        cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                       (data['symbol'], data['volume'], 0, 'ABIERTA'))
    else:
        # Aquí se marca como cerrada
        cursor.execute("UPDATE operaciones SET status = 'CERRADA' WHERE status = 'ABIERTA' AND symbol = ?", (data['symbol'],))
        
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

# Endpoint para consultar cuánto debe un cliente (el 30%)
@app.get("/api/balance/{cliente_id}")
async def obtener_balance(cliente_id: int):
    # Lógica pendiente de implementar
    return {"cliente": cliente_id, "comision_pendiente": 0.0}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
