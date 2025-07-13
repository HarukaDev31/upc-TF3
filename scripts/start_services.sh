#!/bin/bash

# Script para iniciar la API principal (que incluye WebSocket)
echo "🚀 Iniciando API principal con WebSocket integrado..."

# Función para manejar la señal de terminación
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $API_PID 2>/dev/null
    exit 0
}

# Configurar trap para manejar señales
trap cleanup SIGTERM SIGINT

# Iniciar API principal en background (incluye WebSocket)
echo "📡 Iniciando API principal en puerto 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload False &
API_PID=$!

echo "✅ Servicio iniciado:"
echo "   - API Principal: http://localhost:8000"
echo "   - WebSocket: ws://localhost:8000/ws/{client_id}"
echo "   - Health: http://localhost:8000/health"
echo "   - Documentación: http://localhost:8000/docs"

# Esperar a que el proceso termine
wait $API_PID 