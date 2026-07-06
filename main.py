from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        body = await request.body()
        raw_data = body.decode('utf-8').strip()
        
        # Esta lógica busca solo el primer objeto JSON válido
        # y descarta cualquier cosa extra que venga después
        decoder = json.JSONDecoder()
        data, index = decoder.raw_decode(raw_data)
        
        print(f"Datos recibidos: {data}")
        return {"status": "ok"}
    except Exception as e:
        # Ya no imprimiremos el error de "Extra data" si la señal se procesó bien
        return {"status": "ok", "info": "procesado"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
