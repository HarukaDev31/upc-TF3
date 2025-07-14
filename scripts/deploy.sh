#!/bin/bash

# Script de despliegue automático para Cinemax API
# Uso: ./scripts/deploy.sh

set -e  # Salir si hay algún error

echo "🎬 Iniciando despliegue automático de Cinemax API..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar si git está instalado
if ! command -v git &> /dev/null; then
    error "Git no está instalado. Por favor instala Git primero."
    exit 1
fi

log "Verificando dependencias..."
success "Todas las dependencias están instaladas"

# Crear directorio del proyecto si no existe
PROJECT_DIR="/opt/cinemax-api"
if [ ! -d "$PROJECT_DIR" ]; then
    log "Creando directorio del proyecto..."
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi

# Navegar al directorio del proyecto
cd "$PROJECT_DIR"

# Clonar o actualizar el repositorio
if [ -d ".git" ]; then
    log "Actualizando repositorio existente..."
    git pull origin main
else
    log "Clonando repositorio..."
    git clone https://github.com/tu-usuario/cinemax-api.git .
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    log "Creando archivo .env..."
    cp env.example .env
    warning "Por favor edita el archivo .env con tus configuraciones de producción"
fi

# Crear directorio de logs si no existe
if [ ! -d "logs" ]; then
    log "Creando directorio de logs..."
    mkdir -p logs
fi

# Crear directorio nginx si no existe
if [ ! -d "nginx" ]; then
    log "Creando directorio nginx..."
    mkdir -p nginx
fi

# Dar permisos de ejecución a los scripts
log "Configurando permisos..."
chmod +x scripts/*.sh

# Detener contenedores existentes si están corriendo
log "Deteniendo contenedores existentes..."
docker-compose down --remove-orphans

# Limpiar imágenes no utilizadas
log "Limpiando imágenes Docker no utilizadas..."
docker system prune -f

# Construir y levantar los servicios
log "Construyendo y levantando servicios..."
docker-compose up -d --build

# Esperar a que los servicios estén listos
log "Esperando a que los servicios estén listos..."
sleep 30

# Verificar el estado de los servicios
log "Verificando estado de los servicios..."
docker-compose ps

# Verificar que la API esté respondiendo
log "Verificando que la API esté respondiendo..."
for i in {1..10}; do
    if curl -f http://localhost/health &> /dev/null; then
        success "API está respondiendo correctamente"
        break
    else
        warning "Intento $i: API aún no está lista, esperando..."
        sleep 10
    fi
done

# Mostrar información del despliegue
echo ""
echo "🎉 ¡Despliegue completado exitosamente!"
echo ""
echo "📋 Información del despliegue:"
echo "   🌐 API Principal: http://localhost"
echo "   📚 Documentación: http://localhost/docs"
echo "   🔌 WebSocket: ws://localhost/ws/"
echo "   📊 Grafana: http://localhost:3000 (admin/admin123)"
echo "   🗄️  MongoDB Express: http://localhost:8081 (admin/admin123)"
echo "   🔴 Redis Commander: http://localhost:8082 (admin/admin123)"
echo "   📈 Prometheus: http://localhost:9090"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Ver logs de un servicio: docker-compose logs -f api"
echo "   Reiniciar servicios: docker-compose restart"
echo "   Detener servicios: docker-compose down"
echo "   Actualizar y redeployar: ./scripts/deploy.sh"
echo ""

# Verificar puertos abiertos
log "Verificando puertos abiertos..."
netstat -tulpn | grep -E ':(80|443|3000|8081|8082|9090)' || echo "No se encontraron puertos abiertos"

success "¡Despliegue completado! Tu API de Cinemax está lista para usar." 