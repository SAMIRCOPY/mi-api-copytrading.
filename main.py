from fastapi import FastAPI, Request
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operaciones 
                      (id SERIAL PRIMARY KEY, symbol TEXT, volume REAL, 
                       entry_type INTEGER, accion INTEGER DEFAULT 0, status TEXT)''')
    # Por si la tabla ya existía sin la columna "accion" (de una versión anterior)
    cursor.execute('''ALTER TABLE operaciones ADD COLUMN IF NOT EXISTS accion INTEGER DEFAULT 0''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()


@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        data = await request.json()

        symbol = data.get('symbol')
        volume = data.get('volume')
        tipo   = data.get('type')          # 0 = BUY, 1 = SELL
        accion = data.get('entry', 0)      # 0 = ABRIR, 1 = CERRAR

        if symbol is None or volume is None or tipo is None:
            return {"status": "error", "detail": "Faltan campos symbol/volume/type"}

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO operaciones (symbol, volume, entry_type, accion, status) VALUES (%s, %s, %s, %s, %s)",
            (symbol, volume, tipo, accion, 'ABIERTA')
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/get-signals")
async def obtener_senales():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, volume, entry_type, accion FROM operaciones WHERE status = 'ABIERTA'")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Formato exacto que espera el EA esclavo: [id, symbol, volume, type, entry]
    senales = [[row[0], row[1], row[2], row[3], row[4]] for row in rows]

    return {"senales_activas": senales}


@app.get("/confirmar-ejecucion/{id_op}")
@app.post("/confirmar-ejecucion/{id_op}")
async def confirmar_ejecucion(id_op: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE operaciones SET status = 'EJECUTADA' WHERE id = %s", (id_op,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok", "id": id_op}


@app.get("/clear-signals")
async def limpiar():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operaciones")
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "limpio"}
