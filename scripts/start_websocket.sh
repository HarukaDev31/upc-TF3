#!/bin/bash

# Script para levantar solo el servicio WebSocket
echo "🚀 Iniciando servicio WebSocket..."

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Inicia Docker primero."
    exit 1
fi

# Verificar si el puerto 8001 está disponible
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Puerto 8001 está en uso. Deteniendo proceso..."
    sudo lsof -ti:8001 | xargs kill -9
    sleep 2
fi

# Levantar solo Redis y API (que incluye WebSocket)
echo "📦 Levantando Redis y API (con WebSocket)..."
docker-compose up -d redis api

# Esperar a que Redis esté listo
echo "⏳ Esperando a que Redis esté listo..."
until docker-compose exec redis redis-cli ping > /dev/null 2>&1; do
    echo "   Esperando Redis..."
    sleep 2
done
echo "✅ Redis está listo"

# Esperar a que API esté listo
echo "⏳ Esperando a que API esté listo..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "   Esperando API..."
    sleep 2
done
echo "✅ API está listo"

# Esperar a que WebSocket esté listo
echo "⏳ Esperando a que WebSocket esté listo..."
until curl -f http://localhost:8001/health > /dev/null 2>&1; do
    echo "   Esperando WebSocket..."
    sleep 2
done
echo "✅ WebSocket está listo"

echo ""
echo "🎉 Servicio WebSocket iniciado exitosamente!"
echo ""
echo "📊 URLs disponibles:"
echo "   WebSocket: ws://localhost:8001/ws/{client_id}"
echo "   Health: http://localhost:8001/health"
echo "   Stats: http://localhost:8001/stats"
echo ""
echo "🧪 Para probar:"
echo "   python test_websocket_service.py"
echo "   python test_websocket_service.py interactive"
echo "   python test_websocket_service.py multi"
echo ""
echo "📝 Logs:"
echo "   docker-compose logs -f api"
echo ""
echo "🛑 Para detener:"
echo "   docker-compose stop api" 