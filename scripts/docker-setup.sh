#!/bin/bash

# Script de configuración para Docker del Sistema de Cine
# Este script automatiza la configuración inicial

set -e  # Salir si hay algún error

echo "🎬 Sistema de Cine - Docker Setup"
echo "=================================="

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    echo "   Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    echo "   Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker y Docker Compose encontrados"

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p logs
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Verificar si los archivos de configuración existen
if [ ! -f "monitoring/prometheus.yml" ]; then
    echo "❌ Archivo monitoring/prometheus.yml no encontrado"
    exit 1
fi

if [ ! -f "scripts/mongo-init.js" ]; then
    echo "❌ Archivo scripts/mongo-init.js no encontrado"
    exit 1
fi

echo "✅ Archivos de configuración encontrados"

# Construir e iniciar los servicios
echo "🐳 Construyendo e iniciando servicios..."

# Detener contenedores existentes si los hay
docker-compose down

# Construir las imágenes
docker-compose build

# Iniciar los servicios
docker-compose up -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 30

# Verificar el estado de los servicios
echo "🔍 Verificando estado de los servicios..."

# Verificar API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API está funcionando en http://localhost:8000"
else
    echo "❌ API no está respondiendo"
fi

# Verificar MongoDB
if docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB está funcionando"
else
    echo "❌ MongoDB no está respondiendo"
fi

# Verificar Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis está funcionando"
else
    echo "❌ Redis no está respondiendo"
fi

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Servicios disponibles:"
echo "   🎬 API: http://localhost:8000"
echo "   📚 Documentación: http://localhost:8000/docs"
echo "   🗄️  MongoDB Express: http://localhost:8081 (admin/admin123)"
echo "   🔴 Redis Commander: http://localhost:8082 (admin/admin123)"
echo "   📊 Grafana: http://localhost:3000 (admin/admin123)"
echo "   📈 Prometheus: http://localhost:9090"
echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Detener: docker-compose down"
echo "   Reiniciar: docker-compose restart"
echo "   Reconstruir: docker-compose up --build"
echo ""
echo "💡 Tips:"
echo "   • Los datos se persisten en volúmenes Docker"
echo "   • Para desarrollo, usa: docker-compose -f docker-compose.yml -f docker-compose.override.yml up"
echo "   • Para producción, usa: docker-compose -f docker-compose.yml up -d"
echo ""
echo "🎬 ¡Disfruta del Sistema de Cine!" 