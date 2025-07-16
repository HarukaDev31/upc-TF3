#!/bin/bash

# Script completo para configurar Cloudflare Tunnel SIN DOMINIO - Cinemax API
# Uso: ./setup-complete-tunnel.sh

set -e  # Salir si hay algún error

echo "🌐 Configurando Cloudflare Tunnel completo para Cinemax API..."

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

# Verificar si cloudflared está instalado
if ! command -v cloudflared &> /dev/null; then
    log "Instalando cloudflared..."
    
    # Descargar cloudflared
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    
    # Instalar
    sudo dpkg -i cloudflared-linux-amd64.deb
    
    # Limpiar archivo descargado
    rm cloudflared-linux-amd64.deb
    
    success "cloudflared instalado correctamente"
else
    success "cloudflared ya está instalado"
fi

# Crear script para API principal
log "Creando script para API principal..."
cat > ~/start-api-tunnel.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando túnel para API Principal..."

# Verificar que la API esté corriendo
if ! curl -f http://localhost:8080/health &> /dev/null; then
    echo "❌ La API no está respondiendo en localhost:8080"
    echo "💡 Asegúrate de que docker-compose esté corriendo"
    echo "💡 O inicia tu API manualmente"
    exit 1
fi

echo "✅ API respondiendo correctamente"
echo "🌐 Iniciando túnel rápido..."
echo "📝 Presiona Ctrl+C para detener el túnel"

# Iniciar túnel rápido (no requiere dominio)
cloudflared tunnel --url http://localhost:8080
EOF

# Crear script para Grafana
log "Creando script para Grafana..."
cat > ~/start-grafana-tunnel.sh << 'EOF'
#!/bin/bash
echo "📊 Iniciando túnel para Grafana..."

# Verificar que Grafana esté corriendo
if ! curl -f http://localhost:3000 &> /dev/null; then
    echo "❌ Grafana no está respondiendo en localhost:3000"
    echo "💡 Asegúrate de que docker-compose esté corriendo"
    exit 1
fi

echo "✅ Grafana respondiendo correctamente"
echo "🌐 Iniciando túnel rápido..."
echo "📝 Presiona Ctrl+C para detener el túnel"

cloudflared tunnel --url http://localhost:3000
EOF

# Crear script para MongoDB Express
log "Creando script para MongoDB Express..."
cat > ~/start-mongo-tunnel.sh << 'EOF'
#!/bin/bash
echo "🗄️ Iniciando túnel para MongoDB Express..."

# Verificar que MongoDB Express esté corriendo (interfaz web)
if curl -s -L -A "Mozilla/5.0" http://localhost:8081 | grep -q -E "(html|HTML|<!DOCTYPE)" &> /dev/null; then
    echo "✅ MongoDB Express respondiendo correctamente (interfaz web)"
elif nc -z localhost 8081 2>/dev/null; then
    echo "✅ MongoDB Express respondiendo (puerto abierto)"
else
    echo "❌ MongoDB Express no está respondiendo en localhost:8081"
    echo "💡 Asegúrate de que docker-compose esté corriendo"
    echo "💡 Verifica: docker ps | grep mongo-express"
    exit 1
fi

echo "🌐 Iniciando túnel rápido..."
echo "📝 Presiona Ctrl+C para detener el túnel"

cloudflared tunnel --url http://localhost:8081
EOF

# Crear script para Redis Commander
log "Creando script para Redis Commander..."
cat > ~/start-redis-tunnel.sh << 'EOF'
#!/bin/bash
echo "🔴 Iniciando túnel para Redis Commander..."

# Verificar que Redis Commander esté corriendo (interfaz web)
if curl -s -L -A "Mozilla/5.0" http://localhost:8082 | grep -q -E "(html|HTML|<!DOCTYPE)" &> /dev/null; then
    echo "✅ Redis Commander respondiendo correctamente (interfaz web)"
elif nc -z localhost 8082 2>/dev/null; then
    echo "✅ Redis Commander respondiendo (puerto abierto)"
else
    echo "❌ Redis Commander no está respondiendo en localhost:8082"
    echo "💡 Asegúrate de que docker-compose esté corriendo"
    echo "💡 Verifica: docker ps | grep redis-commander"
    exit 1
fi

echo "🌐 Iniciando túnel rápido..."
echo "📝 Presiona Ctrl+C para detener el túnel"

cloudflared tunnel --url http://localhost:8082
EOF

# Crear script para Prometheus
log "Creando script para Prometheus..."
cat > ~/start-prometheus-tunnel.sh << 'EOF'
#!/bin/bash
echo "📈 Iniciando túnel para Prometheus..."

# Verificar que Prometheus esté corriendo
if ! curl -f http://localhost:9090 &> /dev/null; then
    echo "❌ Prometheus no está respondiendo en localhost:9090"
    echo "💡 Asegúrate de que docker-compose esté corriendo"
    exit 1
fi

echo "✅ Prometheus respondiendo correctamente"
echo "🌐 Iniciando túnel rápido..."
echo "📝 Presiona Ctrl+C para detener el túnel"

cloudflared tunnel --url http://localhost:9090
EOF

# Crear script maestro para iniciar todos los túneles SIN DUPLICADOS
log "Creando script maestro para todos los túneles (sin duplicados)..."
cat > ~/start-all-tunnels.sh << 'EOF'
#!/bin/bash

echo "🚀 Iniciando todos los túneles de Cinemax API (sin duplicados)..."

# Función para limpiar túneles existentes
cleanup_existing_tunnels() {
    echo "🛑 Limpiando túneles existentes para evitar duplicados..."
    
    # Matar todos los procesos cloudflared
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    
    # Esperar un momento para que se detengan
    sleep 3
    
    # Limpiar archivos PID y logs antiguos
    rm -f ~/tunnel-*.pid ~/tunnel-*.log
    
    echo "✅ Túneles anteriores limpiados"
    echo ""
}

# Función para verificar si un túnel ya existe para un puerto
check_existing_tunnel() {
    local port=$1
    if pgrep -f "cloudflared tunnel --url http://localhost:$port" > /dev/null; then
        return 0  # Ya existe
    else
        return 1  # No existe
    fi
}

# Función para iniciar túnel único
start_tunnel() {
    local port=$1
    local name=$2
    local service_name=$3
    
    echo "🌐 Verificando $service_name (puerto $port)..."
    
    # Verificar si ya existe túnel para este puerto
    if check_existing_tunnel $port; then
        echo "⚠️  Ya existe un túnel para puerto $port, omitiendo..."
        return
    fi
    
    # Verificar que el servicio esté corriendo
    if curl -f http://localhost:$port &> /dev/null; then
        echo "✅ $service_name está corriendo"
    elif curl -s -L -A "Mozilla/5.0" http://localhost:$port | grep -q -E "(html|HTML|<!DOCTYPE)" &> /dev/null; then
        echo "✅ $service_name está corriendo (interfaz web)"
    elif nc -z localhost $port 2>/dev/null; then
        echo "✅ $service_name está corriendo (puerto abierto)"
    else
        echo "❌ $service_name no está respondiendo en puerto $port"
        echo "💡 Asegúrate de que docker-compose esté corriendo"
        return
    fi
    
    # Iniciar túnel en background
    nohup cloudflared tunnel --url http://localhost:$port > ~/tunnel-$name.log 2>&1 &
    local tunnel_pid=$!
    echo $tunnel_pid > ~/tunnel-$name.pid
    
    # Esperar a que el túnel se estabilice
    sleep 5
    
    # Verificar que el túnel se inició correctamente
    if kill -0 $tunnel_pid 2>/dev/null; then
        echo "📝 Túnel para $service_name iniciado (PID: $tunnel_pid)"
        
        # Intentar obtener la URL del log
        if [ -f ~/tunnel-$name.log ]; then
            # Esperar un poco más para que aparezca la URL
            sleep 2
            url=$(grep -o 'https://.*\.trycloudflare\.com' ~/tunnel-$name.log | head -1)
            if [ ! -z "$url" ]; then
                echo "🌐 $service_name URL: $url"
            else
                echo "⏳ URL generándose... revisa: tail -f ~/tunnel-$name.log"
            fi
        fi
    else
        echo "❌ Error iniciando túnel para $service_name"
        rm -f ~/tunnel-$name.pid
    fi
        
        # Iniciar túnel en background
        nohup cloudflared tunnel --url http://localhost:$port > ~/tunnel-$name.log 2>&1 &
        local tunnel_pid=$!
        echo $tunnel_pid > ~/tunnel-$name.pid
        
        # Esperar a que el túnel se estabilice
        sleep 5
        
        # Verificar que el túnel se inició correctamente
        if kill -0 $tunnel_pid 2>/dev/null; then
            echo "📝 Túnel para $service_name iniciado (PID: $tunnel_pid)"
            
            # Intentar obtener la URL del log
            if [ -f ~/tunnel-$name.log ]; then
                # Esperar un poco más para que aparezca la URL
                sleep 2
                url=$(grep -o 'https://.*\.trycloudflare\.com' ~/tunnel-$name.log | head -1)
                if [ ! -z "$url" ]; then
                    echo "🌐 $service_name URL: $url"
                else
                    echo "⏳ URL generándose... revisa: tail -f ~/tunnel-$name.log"
                fi
            fi
        else
            echo "❌ Error iniciando túnel para $service_name"
            rm -f ~/tunnel-$name.pid
        fi
    else
        echo "❌ $service_name no está respondiendo en puerto $port"
        echo "💡 Asegúrate de que docker-compose esté corriendo"
    fi
    echo ""
}

# Función para mostrar resumen de túneles activos
show_tunnel_summary() {
    echo "📋 Resumen de túneles activos:"
    local active_count=0
    
    for service in api grafana mongo redis prometheus; do
        if [ -f ~/tunnel-$service.pid ]; then
            pid=$(cat ~/tunnel-$service.pid)
            if kill -0 $pid 2>/dev/null; then
                active_count=$((active_count + 1))
                if [ -f ~/tunnel-$service.log ]; then
                    url=$(grep -o 'https://.*\.trycloudflare\.com' ~/tunnel-$service.log | head -1)
                    if [ ! -z "$url" ]; then
                        case $service in
                            api) echo "   🌐 API Principal: $url" ;;
                            grafana) echo "   📊 Grafana: $url" ;;
                            mongo) echo "   🗄️  MongoDB Express: $url" ;;
                            redis) echo "   🔴 Redis Commander: $url" ;;
                            prometheus) echo "   📈 Prometheus: $url" ;;
                        esac
                    else
                        echo "   ⏳ $service: URL generándose..."
                    fi
                fi
            fi
        fi
    done
    
    if [ $active_count -eq 0 ]; then
        echo "   ❌ No hay túneles activos"
    else
        echo ""
        echo "✅ Total de túneles activos: $active_count"
    fi
}

# Crear directorio para logs si no existe
mkdir -p ~/tunnel-logs

# Limpiar túneles existentes primero
cleanup_existing_tunnels

echo "🔍 Verificando servicios disponibles..."
echo ""

# Iniciar túneles para servicios disponibles (uno por uno para evitar conflictos)
start_tunnel "8080" "api" "API Principal"
start_tunnel "3000" "grafana" "Grafana"
start_tunnel "8081" "mongo" "MongoDB Express"
start_tunnel "8082" "redis" "Redis Commander"
start_tunnel "9090" "prometheus" "Prometheus"

echo "🎉 ¡Proceso completado!"
echo ""

# Mostrar resumen final
show_tunnel_summary

echo ""
echo "📋 Para ver logs en tiempo real:"
echo "   📝 API Principal: tail -f ~/tunnel-api.log"
echo "   📝 Grafana: tail -f ~/tunnel-grafana.log"
echo "   📝 MongoDB Express: tail -f ~/tunnel-mongo.log"
echo "   📝 Redis Commander: tail -f ~/tunnel-redis.log"
echo "   📝 Prometheus: tail -f ~/tunnel-prometheus.log"
echo ""
echo "🛑 Para detener todos los túneles:"
echo "   ~/stop-all-tunnels.sh"
echo ""
echo "💡 Si algún túnel no muestra URL, espera unos segundos y ejecuta:"
echo "   tail -f ~/tunnel-<servicio>.log"
EOF

# Crear script para detener todos los túneles
log "Creando script para detener túneles..."
cat > ~/stop-all-tunnels.sh << 'EOF'
#!/bin/bash

echo "🛑 Deteniendo todos los túneles de Cloudflare..."

# Mostrar túneles activos antes de detenerlos
echo "📋 Túneles activos:"
if pgrep cloudflared > /dev/null; then
    ps aux | grep cloudflared | grep -v grep | while read line; do
        echo "   🔸 $line"
    done
else
    echo "   ℹ️  No hay túneles corriendo"
fi
echo ""

# Detener túneles por PID
for service in api grafana mongo redis prometheus; do
    if [ -f ~/tunnel-$service.pid ]; then
        pid=$(cat ~/tunnel-$service.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "🛑 Deteniendo túnel $service (PID: $pid)"
            kill $pid
            rm ~/tunnel-$service.pid
        else
            echo "⚠️  Túnel $service no estaba corriendo"
            rm ~/tunnel-$service.pid 2>/dev/null
        fi
    fi
done

# Buscar y matar cualquier proceso cloudflared restante
echo ""
echo "🔍 Limpiando procesos cloudflared restantes..."
if pgrep -f "cloudflared tunnel" > /dev/null; then
    pkill -f "cloudflared tunnel"
    sleep 2
    
    # Verificar si aún quedan procesos
    if pgrep -f "cloudflared tunnel" > /dev/null; then
        echo "⚠️  Algunos procesos necesitan fuerza bruta..."
        pkill -9 -f "cloudflared tunnel"
    fi
    echo "✅ Todos los procesos cloudflared detenidos"
else
    echo "ℹ️  No hay procesos cloudflared corriendo"
fi

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -f ~/tunnel-*.pid

# Preguntar sobre logs solo si existen
if ls ~/tunnel-*.log >/dev/null 2>&1; then
    read -p "¿Deseas limpiar los archivos de log? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f ~/tunnel-*.log
        echo "🧹 Archivos de log limpiados"
    else
        echo "📁 Archivos de log conservados"
    fi
fi

echo ""
echo "✅ Todos los túneles detenidos correctamente"

# Verificar que todo esté limpio
remaining=$(pgrep -f "cloudflared tunnel" | wc -l)
if [ $remaining -eq 0 ]; then
    echo "🎉 Sistema limpio - No hay procesos cloudflared corriendo"
else
    echo "⚠️  Advertencia: Aún hay $remaining proceso(s) cloudflared corriendo"
    echo "💡 Ejecuta: ps aux | grep cloudflared"
fi
EOF

# Crear script de ayuda
log "Creando script de ayuda..."
cat > ~/tunnel-help.sh << 'EOF'
#!/bin/bash

echo "🌐 Cloudflare Tunnel - Cinemax API"
echo "=================================="
echo ""
echo "📋 Scripts disponibles:"
echo "   🌐 API Principal: ~/start-api-tunnel.sh"
echo "   📊 Grafana: ~/start-grafana-tunnel.sh"
echo "   🗄️  MongoDB Express: ~/start-mongo-tunnel.sh"
echo "   🔴 Redis Commander: ~/start-redis-tunnel.sh"
echo "   📈 Prometheus: ~/start-prometheus-tunnel.sh"
echo ""
echo "🚀 Scripts maestros:"
echo "   🚀 Iniciar todos: ~/start-all-tunnels.sh"
echo "   🛑 Detener todos: ~/stop-all-tunnels.sh"
echo "   ❓ Ayuda: ~/tunnel-help.sh"
echo ""
echo "💡 Uso típico:"
echo "   1. Iniciar docker-compose con tus servicios"
echo "   2. Ejecutar: ~/start-all-tunnels.sh"
echo "   3. Copiar las URLs generadas"
echo "   4. Cuando termines: ~/stop-all-tunnels.sh"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: tail -f ~/tunnel-api.log"
echo "   Ver procesos: ps aux | grep cloudflared"
echo "   Verificar puertos: netstat -tlnp | grep :8080"
echo ""
EOF

# Crear script de verificación de servicios mejorado
log "Creando script de verificación mejorado..."
cat > ~/check-services.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificando servicios de Cinemax API..."
echo ""

# Función para verificar servicio API/HTTP
check_service() {
    local port=$1
    local name=$2
    
    if curl -f http://localhost:$port &> /dev/null; then
        echo "✅ $name está corriendo en puerto $port"
        return 0
    else
        echo "❌ $name NO está corriendo en puerto $port"
        return 1
    fi
}

# Función para verificar servicios web (que requieren navegador)
check_web_service() {
    local port=$1
    local name=$2
    local path=$3
    
    # Usar curl con user-agent de navegador y seguir redirects
    if curl -s -L -A "Mozilla/5.0" http://localhost:$port$path | grep -q -E "(html|HTML|<!DOCTYPE)" &> /dev/null; then
        echo "✅ $name está corriendo en puerto $port (interfaz web)"
        return 0
    elif nc -z localhost $port 2>/dev/null; then
        echo "✅ $name está corriendo en puerto $port (puerto abierto)"
        return 0
    else
        echo "❌ $name NO está corriendo en puerto $port"
        return 1
    fi
}

# Función para verificar contenedores Docker
check_docker_container() {
    local container_name=$1
    local service_name=$2
    
    if docker ps | grep -q "$container_name.*Up"; then
        echo "✅ Contenedor $service_name está corriendo"
        return 0
    else
        echo "❌ Contenedor $service_name NO está corriendo"
        return 1
    fi
}

# Función para verificar túneles activos
check_tunnels() {
    echo ""
    echo "🌐 Verificando túneles activos..."
    
    local tunnel_count=0
    for service in api grafana mongo redis prometheus; do
        if [ -f ~/tunnel-$service.pid ]; then
            pid=$(cat ~/tunnel-$service.pid)
            if kill -0 $pid 2>/dev/null; then
                tunnel_count=$((tunnel_count + 1))
                echo "✅ Túnel $service activo (PID: $pid)"
                
                # Mostrar URL si está disponible
                if [ -f ~/tunnel-$service.log ]; then
                    url=$(grep -o 'https://.*\.trycloudflare\.com' ~/tunnel-$service.log | head -1)
                    if [ ! -z "$url" ]; then
                        echo "   🌐 URL: $url"
                    fi
                fi
            else
                echo "❌ Túnel $service no está corriendo (PID inválido)"
                rm -f ~/tunnel-$service.pid
            fi
        fi
    done
    
    if [ $tunnel_count -eq 0 ]; then
        echo "❌ No hay túneles activos"
    else
        echo "📊 Total túneles activos: $tunnel_count"
    fi
}

# Función para detectar procesos duplicados
check_duplicates() {
    echo ""
    echo "🔍 Verificando procesos duplicados..."
    
    local cloudflared_count=$(pgrep -f "cloudflared tunnel" | wc -l)
    if [ $cloudflared_count -gt 0 ]; then
        echo "📊 Procesos cloudflared encontrados: $cloudflared_count"
        
        # Mostrar detalles de procesos
        ps aux | grep "cloudflared tunnel" | grep -v grep | while read line; do
            echo "   🔸 $line"
        done
        
        # Detectar duplicados por puerto
        echo ""
        echo "🔍 Detectando duplicados por puerto..."
        for port in 8080 3000 8081 8082 9090; do
            count=$(pgrep -f "cloudflared tunnel --url http://localhost:$port" | wc -l)
            if [ $count -gt 1 ]; then
                echo "⚠️  Puerto $port tiene $count túneles duplicados"
            elif [ $count -eq 1 ]; then
                echo "✅ Puerto $port tiene 1 túnel (correcto)"
            fi
        done
    else
        echo "ℹ️  No hay procesos cloudflared corriendo"
    fi
}

# Verificar todos los servicios
services_running=0
total_services=5

echo "📋 Estado de los servicios:"

# API Principal (Nginx proxy)
check_service "8080" "API Principal (Nginx)" && ((services_running++))

# Grafana (interfaz web)
check_web_service "3000" "Grafana" "/" && ((services_running++))

# MongoDB Express (interfaz web)
check_web_service "8081" "MongoDB Express" "/" && ((services_running++))

# Redis Commander (interfaz web)
check_web_service "8082" "Redis Commander" "/" && ((services_running++))

# Prometheus (API y interfaz web)
check_web_service "9090" "Prometheus" "/" && ((services_running++))

echo ""
echo "📊 Resumen: $services_running/$total_services servicios corriendo"

# Verificar contenedores Docker si está disponible
if command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Estado de contenedores Docker:"
    check_docker_container "cinemax_nginx" "Nginx"
    check_docker_container "cinemax_api" "FastAPI"
    check_docker_container "cinemax_mongodb" "MongoDB"
    check_docker_container "cinemax_redis" "Redis"
    check_docker_container "cinemax_mongo_express" "MongoDB Express"
    check_docker_container "cinemax_redis_commander" "Redis Commander"
    check_docker_container "cinemax_prometheus" "Prometheus"
    check_docker_container "cinemax_grafana" "Grafana"
fi

# Verificar túneles
check_tunnels

# Verificar duplicados
check_duplicates

echo ""
echo "💡 Recomendaciones:"
if [ $services_running -eq 0 ]; then
    echo "   🔄 Ejecuta: docker-compose up -d"
elif [ $services_running -eq $total_services ]; then
    tunnel_count=$(pgrep -f "cloudflared tunnel" | wc -l)
    if [ $tunnel_count -eq 0 ]; then
        echo "   🚀 Todos los servicios están listos. Ejecuta: ./start-all-tunnels.sh"
    elif [ $tunnel_count -gt $total_services ]; then
        echo "   ⚠️  Hay túneles duplicados. Ejecuta: ./stop-all-tunnels.sh"
        echo "   🚀 Luego ejecuta: ./start-all-tunnels.sh"
    else
        echo "   ✅ Todo está funcionando correctamente"
    fi
else
    echo "   ⚠️  Algunos servicios no están corriendo"
    echo "   🔍 Verifica tu docker-compose.yml"
    echo "   🔄 Intenta: docker-compose restart"
fi
EOF

# Hacer todos los scripts ejecutables
chmod +x ~/start-api-tunnel.sh
chmod +x ~/start-grafana-tunnel.sh
chmod +x ~/start-mongo-tunnel.sh
chmod +x ~/start-redis-tunnel.sh
chmod +x ~/start-prometheus-tunnel.sh
chmod +x ~/start-all-tunnels.sh
chmod +x ~/stop-all-tunnels.sh
chmod +x ~/tunnel-help.sh
chmod +x ~/check-services.sh

success "Todos los scripts creados exitosamente"

# Crear enlaces simbólicos en el directorio actual para fácil acceso
ln -sf ~/start-api-tunnel.sh ./start-api-tunnel.sh
ln -sf ~/start-all-tunnels.sh ./start-all-tunnels.sh
ln -sf ~/stop-all-tunnels.sh ./stop-all-tunnels.sh
ln -sf ~/check-services.sh ./check-services.sh
ln -sf ~/tunnel-help.sh ./tunnel-help.sh

success "Enlaces simbólicos creados en el directorio actual"

# Mostrar información final
echo ""
echo "🎉 ¡Cloudflare Tunnel configurado exitosamente!"
echo ""
echo "📋 Scripts disponibles (tanto en ~/ como en directorio actual):"
echo "   🌐 API Principal: ./start-api-tunnel.sh"
echo "   📊 Grafana: ./start-grafana-tunnel.sh"
echo "   🗄️  MongoDB Express: ./start-mongo-tunnel.sh"
echo "   🔴 Redis Commander: ./start-redis-tunnel.sh"
echo "   📈 Prometheus: ./start-prometheus-tunnel.sh"
echo ""
echo "🚀 Scripts maestros:"
echo "   🚀 Iniciar todos: ./start-all-tunnels.sh"
echo "   🛑 Detener todos: ./stop-all-tunnels.sh"
echo "   🔍 Verificar servicios: ./check-services.sh"
echo "   ❓ Ayuda: ./tunnel-help.sh"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Verifica tus servicios: ./check-services.sh"
echo "   2. Inicia los túneles: ./start-all-tunnels.sh"
echo "   3. Usa las URLs generadas para acceder desde internet"
echo ""
echo "📝 Notas importantes:"
echo "   - Cada túnel genera una URL única como https://abc123.trycloudflare.com"
echo "   - Las URLs cambian cada vez que reinicias el túnel"
echo "   - Son perfectas para pruebas y desarrollo"
echo "   - No necesitas dominio propio"
echo "   - Las URLs son públicas pero impredecibles"
echo ""

success "¡Configuración completada! Tu API estará disponible a través de Cloudflare Tunnel."