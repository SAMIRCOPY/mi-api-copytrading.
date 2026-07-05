[main.py.txt](https://github.com/user-attachments/files/29682241/main.py.txt)from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Gold Trading Academy API",
    description="Endpoint receptor de señales para Copy Trading de Oro",
    version="1.0.0"
)

# Definimos la estructura exacta del JSON que envía MetaTrader 5
class SenalTrading(BaseModel):
    symbol: str
    volume: float
    type: int   # 0 = BUY, 1 = SELL
    entry: int  # 0 = Entrada/Apertura, 1 = Salida/Cierre

# Función en segundo plano para procesar la señal (replicar en clientes, enviar a Telegram, etc.)
def procesar_senal_background(senal: SenalTrading):
    tipo_operacion = "COMPRA (BUY)" if senal.type == 0 else "VENTA (SELL)"
    accion = "APERTURA" if senal.entry == 0 else "CIERRE"
    
    print(f"\n--- NUEVA SEÑAL RECIBIDA ---")
    print(f"Activo: {senal.symbol}")
    print(f"Operación: {tipo_operacion}")
    print(f"Volumen: {senal.volume} lotes")
    print(f"Acción: {accion}")
    print(f"----------------------------\n")
    
    # TODO: Aquí conectarás la lógica para enviar esta orden a las cuentas de tus alumnos
    pass

@app.get("/")
def inicio():
    return {"estado": "API de Copy Trading Activa", "academia": "Gold Trading Academy"}

# Endpoint tipo POST que coincide con la URL que pusiste en el EA ('/webhook')
@app.post("/webhook")
async def recibir_webhook(senal: SenalTrading, background_tasks: BackgroundTasks):
    # Verificación básica para asegurar que el símbolo no esté vacío
    if not senal.symbol:
        raise HTTPException(status_code=400, detail="Símbolo inválido")
        
    # Procesamos la tarea en segundo plano para que MetaTrader reciba una respuesta inmediata (menor latencia)
    background_tasks.add_task(procesar_senal_background, senal)
    
    return {
        "status": "success", 
        "message": f"Señal recibida para {senal.symbol}"
    }
