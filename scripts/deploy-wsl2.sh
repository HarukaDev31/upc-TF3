#!/bin/bash

# Script de despliegue automático para Cinemax API en WSL2
# Uso: ./scripts/deploy-wsl2.sh

set -e  # Salir si hay algún error

echo "🎬 Iniciando despliegue automático de Cinemax API en WSL2..."

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

# Obtener IP de WSL2
get_wsl_ip() {
    ip route show | grep default | awk '{print $3}' | head -1
}

# Verificar si estamos en WSL2
check_wsl2() {
    if grep -qi microsoft /proc/version 2>/dev/null; then
        success "Detectado entorno WSL2"
        return 0
    else
        warning "No se detectó entorno WSL2, continuando..."
        return 1
    fi
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    log "Instalando Docker..."
    # Instalar Docker en Ubuntu WSL2
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    sudo systemctl enable docker
    sudo systemctl start docker
    success "Docker instalado correctamente"
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    log "Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    success "Docker Compose instalado correctamente"
fi

# Verificar si git está instalado
if ! command -v git &> /dev/null; then
    log "Instalando Git..."
    sudo apt-get update
    sudo apt-get install -y git
    success "Git instalado correctamente"
fi

log "Verificando dependencias..."
success "Todas las dependencias están instaladas"

# Crear directorio del proyecto
PROJECT_DIR="$HOME/cinemax-api"
if [ ! -d "$PROJECT_DIR" ]; then
    log "Creando directorio del proyecto..."
    mkdir -p "$PROJECT_DIR"
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
    
    # Configurar para desarrollo en WSL2
    sed -i 's/ENVIRONMENT=production/ENVIRONMENT=development/' .env
    sed -i 's/DEBUG=false/DEBUG=true/' .env
    
    warning "Archivo .env creado. Edita las variables de entorno según necesites."
fi

# Crear directorios necesarios
log "Creando directorios..."
mkdir -p logs nginx static

# Dar permisos de ejecución a los scripts
log "Configurando permisos..."
chmod +x scripts/*.sh

# Detener contenedores existentes si están corriendo
log "Deteniendo contenedores existentes..."
docker-compose down --remove-orphans 2>/dev/null || true

# Limpiar imágenes no utilizadas
log "Limpiar imágenes Docker no utilizadas..."
docker system prune -f

# Construir y levantar los servicios
log "Construyendo y levantando servicios..."
docker-compose up -d --build

# Esperar a que los servicios estén listos
log "Esperando a que los servicios estén listos..."
sleep 45

# Verificar el estado de los servicios
log "Verificando estado de los servicios..."
docker-compose ps

# Obtener IP de WSL2
WSL_IP=$(get_wsl_ip)

# Verificar que la API esté respondiendo
log "Verificando que la API esté respondiendo..."
for i in {1..15}; do
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
echo "🎉 ¡Despliegue en WSL2 completado exitosamente!"
echo ""
echo "📋 Información del despliegue:"
echo "   🌐 IP WSL2: $WSL_IP"
echo "   🌐 API Local: http://localhost"
echo "   📚 Documentación: http://localhost/docs"
echo "   🔌 WebSocket: ws://localhost/ws/"
echo "   📊 Grafana: http://localhost:3000 (admin/admin123)"
echo "   🗄️  MongoDB Express: http://localhost:8081 (admin/admin123)"
echo "   🔴 Redis Commander: http://localhost:8082 (admin/admin123)"
echo "   📈 Prometheus: http://localhost:9090"
echo ""
echo "🌍 Para exponer a internet:"
echo "   📝 Configura port forwarding en Windows"
echo "   📝 Usa ngrok o similar para exposición pública"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Ver logs de un servicio: docker-compose logs -f api"
echo "   Reiniciar servicios: docker-compose restart"
echo "   Detener servicios: docker-compose down"
echo "   Actualizar y redeployar: ./scripts/deploy-wsl2.sh"
echo "   Ver estado: docker-compose ps"
echo ""

# Verificar puertos abiertos
log "Verificando puertos abiertos..."
netstat -tulpn | grep -E ':(80|443|3000|8081|8082|9090)' || echo "No se encontraron puertos abiertos"

# Mostrar información de monitoreo
echo "📊 Monitoreo:"
echo "   Health Check: curl http://localhost/health"
echo "   Métricas: curl http://localhost/metrics"
echo "   Logs de Nginx: docker exec cinemax_nginx tail -f /var/log/nginx/access.log"
echo ""

# Configurar reinicio automático
log "Configurando reinicio automático..."
sudo systemctl enable docker
success "Docker configurado para reinicio automático"

success "¡Despliegue en WSL2 completado! Tu API de Cinemax está lista para usar."
echo ""
echo "🌐 Tu API está disponible localmente en: http://localhost"
echo "📝 Para exponer a internet, configura port forwarding o usa ngrok" 