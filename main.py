from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import json

app = FastAPI()

@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        body = await request.body()
        data = json.loads(body)
        print(f"Datos recibidos: {data}")
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
