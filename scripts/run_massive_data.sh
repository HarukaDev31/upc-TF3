#!/bin/bash

# Script para ejecutar la generación de datos masivos
# Genera: 1000 salas, 50k películas, 1M funciones, 100k clientes, 500k transacciones

echo "🎬 Iniciando generación de datos masivos para el Sistema de Cine..."
echo "================================================================"

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    echo "Por favor, inicia Docker Desktop y vuelve a intentar"
    exit 1
fi

# Verificar que los contenedores estén corriendo
if ! docker ps | grep -q "cinemax_mongodb"; then
    echo "❌ Error: Los contenedores no están corriendo"
    echo "Ejecutando: docker-compose up -d"
    docker-compose up -d
    echo "⏳ Esperando que los servicios estén listos..."
    sleep 30
fi

# Verificar que MongoDB esté listo
echo "🔍 Verificando conexión a MongoDB..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec cinemax_mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "✅ MongoDB está listo"
        break
    else
        echo "⏳ Esperando MongoDB... (intento $((attempt + 1))/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Error: MongoDB no está respondiendo después de $max_attempts intentos"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Ejecutar el script de generación de datos masivos
echo "🚀 Ejecutando generación de datos masivos..."
echo "📊 Configuración:"
echo "   - 1,000 salas"
echo "   - 50,000 películas"
echo "   - 1,000,000 funciones"
echo "   - 100,000 clientes"
echo "   - 500,000 transacciones"
echo ""

# Ejecutar el script de MongoDB
echo "⏳ Iniciando generación (esto puede tomar varios minutos)..."
start_time=$(date +%s)

docker exec -i cinemax_mongodb mongosh cinemax < scripts/generate_massive_data.js 2>&1 | tee logs/massive_data_generation.log

end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "================================================================"
echo "✅ Generación de datos masivos completada!"
echo "⏱️  Tiempo total: $((duration / 60)) minutos y $((duration % 60)) segundos"
echo "📁 Logs guardados en: logs/massive_data_generation.log"
echo ""

# Mostrar estadísticas de la base de datos
echo "📊 Estadísticas de la base de datos:"
echo "================================================================"

echo "🏢 Salas:"
docker exec cinemax_mongodb mongosh cinemax --eval "db.salas.countDocuments()" --quiet

echo "🎬 Películas:"
docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.countDocuments()" --quiet

echo "👥 Clientes:"
docker exec cinemax_mongodb mongosh cinemax --eval "db.clientes.countDocuments()" --quiet

echo "🎭 Funciones:"
docker exec cinemax_mongodb mongosh cinemax --eval "db.funciones.countDocuments()" --quiet

echo "💳 Transacciones:"
docker exec cinemax_mongodb mongosh cinemax --eval "db.transacciones.countDocuments()" --quiet

echo ""
echo "🔍 Índices creados:"
docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.getIndexes().length + db.funciones.getIndexes().length + db.transacciones.getIndexes().length + db.clientes.getIndexes().length" --quiet

echo ""
echo "🎬 ¡Tu sistema de cine está listo para pruebas de rendimiento a gran escala!"
echo ""
echo "📊 URLs de monitoreo:"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - MongoDB Express: http://localhost:8081"
echo "   - Redis Commander: http://localhost:8082"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000"
echo ""
echo "🚀 ¡Puedes empezar a probar los endpoints con Postman!" 