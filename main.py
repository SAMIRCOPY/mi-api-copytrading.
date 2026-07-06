@app.post("/api/senal")
async def recibir_senal(request: Request):
    try:
        # Leemos el cuerpo crudo como texto
        body = await request.body()
        body_str = body.decode('utf-8').strip()
        
        # Si el cuerpo viene con caracteres extra, intentamos limpiar
        # Esto soluciona el error de 'Extra data'
        import json
        data = json.loads(body_str)
        
        print(f"Datos recibidos: {data}")
        
        # Conexión a DB y resto de tu lógica...
        conn = sqlite3.connect("trading_data.db")
        cursor = conn.cursor()
        
        symbol = data.get('symbol', 'UNKNOWN')
        volume = data.get('volume', 0.0)
        entry = data.get('entry', 0)
        
        if entry == 0:
            cursor.execute("INSERT INTO operaciones (symbol, volume, entry_type, status) VALUES (?, ?, ?, ?)",
                           (symbol, volume, 0, 'ABIERTA'))
        else:
            cursor.execute("UPDATE operaciones SET status = 'CERRADA' WHERE status = 'ABIERTA' AND symbol = ?", (symbol,))
            
        conn.commit()
        conn.close()
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Error procesando señal: {e}")
        return {"status": "error", "detail": str(e)}
