#!/bin/bash

# Script para iniciar tanto la API principal como el servicio WebSocket
echo "🚀 Iniciando servicios..."

# Función para manejar la señal de terminación
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $API_PID $WEBSOCKET_PID 2>/dev/null
    exit 0
}

# Configurar trap para manejar señales
trap cleanup SIGTERM SIGINT

# Iniciar API principal en background
echo "📡 Iniciando API principal en puerto 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload False &
API_PID=$!

# Esperar un poco para que la API se inicie
sleep 3

# Iniciar servicio WebSocket en background
echo "🔌 Iniciando servicio WebSocket en puerto 8001..."
python -m services.websocket_service &
WEBSOCKET_PID=$!

echo "✅ Ambos servicios iniciados:"
echo "   - API Principal: http://localhost:8000"
echo "   - WebSocket: ws://localhost:8001/ws/{client_id}"
echo "   - Health WebSocket: http://localhost:8001/health"

# Esperar a que ambos procesos terminen
wait $API_PID $WEBSOCKET_PID 