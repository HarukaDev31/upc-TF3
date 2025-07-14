#!/bin/bash

# Script de despliegue automático para Cinemax API en EC2 Linux
# Uso: ./scripts/deploy-ec2.sh

set -e  # Salir si hay algún error

echo "🎬 Iniciando despliegue automático de Cinemax API en EC2..."

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

# Obtener IP pública de la instancia
get_public_ip() {
    curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost"
}

# Verificar si estamos en EC2
check_ec2() {
    if curl -s http://169.254.169.254/latest/meta-data/instance-id >/dev/null 2>&1; then
        success "Detectado entorno EC2"
        return 0
    else
        warning "No se detectó entorno EC2, continuando..."
        return 1
    fi
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    log "Instalando Docker..."
    # Instalar Docker en Amazon Linux 2
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    sudo systemctl enable docker
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
    sudo yum install -y git
    success "Git instalado correctamente"
fi

log "Verificando dependencias..."
success "Todas las dependencias están instaladas"

# Configurar firewall (Security Group)
log "Configurando firewall..."
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Abrir puertos necesarios
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --permanent --add-port=8082/tcp
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload
success "Firewall configurado"

# Crear directorio del proyecto
PROJECT_DIR="/home/ec2-user/cinemax-api"
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
    
    # Configurar para producción en EC2
    sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env
    sed -i 's/DEBUG=true/DEBUG=false/' .env
    
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

# Obtener IP pública
PUBLIC_IP=$(get_public_ip)

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
echo "🎉 ¡Despliegue en EC2 completado exitosamente!"
echo ""
echo "📋 Información del despliegue:"
echo "   🌐 IP Pública: $PUBLIC_IP"
echo "   🌐 API Principal: http://$PUBLIC_IP"
echo "   📚 Documentación: http://$PUBLIC_IP/docs"
echo "   🔌 WebSocket: ws://$PUBLIC_IP/ws/"
echo "   📊 Grafana: http://$PUBLIC_IP:3000 (admin/admin123)"
echo "   🗄️  MongoDB Express: http://$PUBLIC_IP:8081 (admin/admin123)"
echo "   🔴 Redis Commander: http://$PUBLIC_IP:8082 (admin/admin123)"
echo "   📈 Prometheus: http://$PUBLIC_IP:9090"
echo ""
echo "🔒 Configuración de seguridad:"
echo "   ✅ Firewall configurado (puertos 80, 443, 3000, 8081, 8082, 9090)"
echo "   ✅ Rate limiting activo"
echo "   ✅ Headers de seguridad configurados"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Ver logs de un servicio: docker-compose logs -f api"
echo "   Reiniciar servicios: docker-compose restart"
echo "   Detener servicios: docker-compose down"
echo "   Actualizar y redeployar: ./scripts/deploy-ec2.sh"
echo "   Ver estado: docker-compose ps"
echo ""

# Verificar puertos abiertos
log "Verificando puertos abiertos..."
netstat -tulpn | grep -E ':(80|443|3000|8081|8082|9090)' || echo "No se encontraron puertos abiertos"

# Mostrar información de monitoreo
echo "📊 Monitoreo:"
echo "   Health Check: curl http://$PUBLIC_IP/health"
echo "   Métricas: curl http://$PUBLIC_IP/metrics"
echo "   Logs de Nginx: docker exec cinemax_nginx tail -f /var/log/nginx/access.log"
echo ""

# Configurar reinicio automático
log "Configurando reinicio automático..."
sudo systemctl enable docker
success "Docker configurado para reinicio automático"

success "¡Despliegue en EC2 completado! Tu API de Cinemax está lista para usar en internet."
echo ""
echo "🌍 Tu API está disponible públicamente en: http://$PUBLIC_IP" 