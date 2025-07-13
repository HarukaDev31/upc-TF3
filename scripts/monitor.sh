#!/bin/bash

# Script de monitoreo continuo del Sistema de Cine
# Monitorea métricas en tiempo real

echo "📊 Iniciando monitoreo continuo del Sistema de Cine..."
echo "================================================================"

# Configuración
BASE_URL="http://localhost:8000"
LOG_DIR="logs"
MONITOR_LOG="$LOG_DIR/monitor_$(date +%Y%m%d_%H%M%S).log"
INTERVAL=30  # Segundos entre mediciones

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Función para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MONITOR_LOG"
}

# Función para obtener métricas de la API
get_api_metrics() {
    local start=$(date +%s%N)
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/health" -o /dev/null)
    local end=$(date +%s%N)
    local duration=$(( (end - start) / 1000000 ))
    
    echo "$response:$duration"
}

# Función para obtener métricas de Docker
get_docker_metrics() {
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Función para obtener métricas de MongoDB
get_mongodb_metrics() {
    docker exec cinemax_mongodb mongosh cinemax --eval "
        db.stats()
    " --quiet 2>/dev/null
}

# Función para obtener métricas de Redis
get_redis_metrics() {
    docker exec cinemax_redis redis-cli INFO memory 2>/dev/null
}

# Función para obtener métricas de Prometheus
get_prometheus_metrics() {
    curl -s "http://localhost:9090/api/v1/query?query=up" 2>/dev/null
}

# Función para mostrar métricas en tiempo real
show_realtime_metrics() {
    clear
    echo "📊 MONITOREO EN TIEMPO REAL - Sistema de Cine"
    echo "================================================================"
    echo "Última actualización: $(date)"
    echo ""
    
    # Métricas de la API
    echo "🏥 ESTADO DE LA API:"
    api_metrics=$(get_api_metrics)
    http_code=$(echo $api_metrics | cut -d: -f1)
    response_time=$(echo $api_metrics | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ API funcionando - Tiempo de respuesta: ${response_time}ms"
    else
        echo "   ❌ API no responde - HTTP: $http_code"
    fi
    
    echo ""
    
    # Métricas de Docker
    echo "🐳 MÉTRICAS DE DOCKER:"
    get_docker_metrics | while read line; do
        echo "   $line"
    done
    
    echo ""
    
    # Métricas de base de datos
    echo "🗄️  MÉTRICAS DE MONGODB:"
    mongodb_stats=$(get_mongodb_metrics)
    if [ -n "$mongodb_stats" ]; then
        echo "   ✅ MongoDB conectado"
        # Extraer información relevante
        collections=$(echo "$mongodb_stats" | grep "collections" | head -1)
        data_size=$(echo "$mongodb_stats" | grep "dataSize" | head -1)
        echo "   $collections"
        echo "   $data_size"
    else
        echo "   ❌ MongoDB no disponible"
    fi
    
    echo ""
    
    # Métricas de Redis
    echo "🚀 MÉTRICAS DE REDIS:"
    redis_info=$(get_redis_metrics)
    if [ -n "$redis_info" ]; then
        echo "   ✅ Redis conectado"
        # Extraer información relevante
        used_memory=$(echo "$redis_info" | grep "used_memory_human" | cut -d: -f2)
        connected_clients=$(echo "$redis_info" | grep "connected_clients" | cut -d: -f2)
        echo "   Memoria usada: $used_memory"
        echo "   Clientes conectados: $connected_clients"
    else
        echo "   ❌ Redis no disponible"
    fi
    
    echo ""
    
    # Métricas de Prometheus
    echo "📈 MÉTRICAS DE PROMETHEUS:"
    prometheus_status=$(get_prometheus_metrics)
    if [ -n "$prometheus_status" ]; then
        echo "   ✅ Prometheus funcionando"
    else
        echo "   ❌ Prometheus no disponible"
    fi
    
    echo ""
    echo "================================================================"
    echo "Presiona Ctrl+C para detener el monitoreo"
    echo "Logs guardados en: $MONITOR_LOG"
}

# Función para monitoreo continuo
continuous_monitoring() {
    log "📊 Iniciando monitoreo continuo..."
    
    while true; do
        # Obtener métricas
        api_metrics=$(get_api_metrics)
        http_code=$(echo $api_metrics | cut -d: -f1)
        response_time=$(echo $api_metrics | cut -d: -f2)
        
        # Log de métricas
        log "API: HTTP $http_code, Tiempo: ${response_time}ms"
        
        # Verificar alertas
        if [ "$http_code" != "200" ]; then
            log "🚨 ALERTA: API no responde correctamente (HTTP: $http_code)"
        fi
        
        if [ $response_time -gt 5000 ]; then
            log "⚠️  ADVERTENCIA: Tiempo de respuesta lento (${response_time}ms)"
        fi
        
        # Obtener métricas de Docker
        docker_stats=$(get_docker_metrics)
        log "Docker: $docker_stats"
        
        # Obtener métricas de MongoDB
        mongodb_stats=$(get_mongodb_metrics)
        if [ -n "$mongodb_stats" ]; then
            log "MongoDB: Conectado"
        else
            log "🚨 ALERTA: MongoDB no disponible"
        fi
        
        # Obtener métricas de Redis
        redis_info=$(get_redis_metrics)
        if [ -n "$redis_info" ]; then
            log "Redis: Conectado"
        else
            log "🚨 ALERTA: Redis no disponible"
        fi
        
        # Esperar antes de la siguiente medición
        sleep $INTERVAL
    done
}

# Función para mostrar dashboard en tiempo real
show_dashboard() {
    log "📊 Mostrando dashboard en tiempo real..."
    
    while true; do
        show_realtime_metrics
        sleep $INTERVAL
    done
}

# Función para generar reporte de métricas
generate_metrics_report() {
    log "📋 Generando reporte de métricas..."
    
    echo "================================================================" | tee -a "$MONITOR_LOG"
    echo "📊 REPORTE DE MÉTRICAS - Sistema de Cine" | tee -a "$MONITOR_LOG"
    echo "Fecha: $(date)" | tee -a "$MONITOR_LOG"
    echo "================================================================" | tee -a "$MONITOR_LOG"
    
    # Métricas de la API
    echo "🏥 MÉTRICAS DE LA API:" | tee -a "$MONITOR_LOG"
    api_metrics=$(get_api_metrics)
    http_code=$(echo $api_metrics | cut -d: -f1)
    response_time=$(echo $api_metrics | cut -d: -f2)
    echo "   HTTP Code: $http_code" | tee -a "$MONITOR_LOG"
    echo "   Tiempo de respuesta: ${response_time}ms" | tee -a "$MONITOR_LOG"
    
    # Métricas de Docker
    echo "" | tee -a "$MONITOR_LOG"
    echo "🐳 MÉTRICAS DE DOCKER:" | tee -a "$MONITOR_LOG"
    get_docker_metrics | tee -a "$MONITOR_LOG"
    
    # Métricas de MongoDB
    echo "" | tee -a "$MONITOR_LOG"
    echo "🗄️  MÉTRICAS DE MONGODB:" | tee -a "$MONITOR_LOG"
    get_mongodb_metrics | tee -a "$MONITOR_LOG"
    
    # Métricas de Redis
    echo "" | tee -a "$MONITOR_LOG"
    echo "🚀 MÉTRICAS DE REDIS:" | tee -a "$MONITOR_LOG"
    get_redis_metrics | tee -a "$MONITOR_LOG"
    
    # URLs de monitoreo
    echo "" | tee -a "$MONITOR_LOG"
    echo "📊 URLs DE MONITOREO:" | tee -a "$MONITOR_LOG"
    echo "   - API Docs: http://localhost:8000/docs" | tee -a "$MONITOR_LOG"
    echo "   - MongoDB Express: http://localhost:8081" | tee -a "$MONITOR_LOG"
    echo "   - Redis Commander: http://localhost:8082" | tee -a "$MONITOR_LOG"
    echo "   - Prometheus: http://localhost:9090" | tee -a "$MONITOR_LOG"
    echo "   - Grafana: http://localhost:3000" | tee -a "$MONITOR_LOG"
    
    echo "" | tee -a "$MONITOR_LOG"
    echo "📁 Logs guardados en: $MONITOR_LOG" | tee -a "$MONITOR_LOG"
    echo "================================================================" | tee -a "$MONITOR_LOG"
}

# Función para monitoreo con alertas
monitor_with_alerts() {
    log "🚨 Iniciando monitoreo con alertas..."
    
    while true; do
        # Verificar API
        api_metrics=$(get_api_metrics)
        http_code=$(echo $api_metrics | cut -d: -f1)
        response_time=$(echo $api_metrics | cut -d: -f2)
        
        # Alertas de API
        if [ "$http_code" != "200" ]; then
            log "🚨 CRÍTICO: API no responde (HTTP: $http_code)"
            # Aquí podrías enviar notificaciones (email, Slack, etc.)
        fi
        
        if [ $response_time -gt 10000 ]; then
            log "🚨 CRÍTICO: Tiempo de respuesta muy lento (${response_time}ms)"
        elif [ $response_time -gt 5000 ]; then
            log "⚠️  ADVERTENCIA: Tiempo de respuesta lento (${response_time}ms)"
        fi
        
        # Verificar servicios
        if ! docker exec cinemax_mongodb mongosh --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
            log "🚨 CRÍTICO: MongoDB no responde"
        fi
        
        if ! docker exec cinemax_redis redis-cli ping > /dev/null 2>&1; then
            log "🚨 CRÍTICO: Redis no responde"
        fi
        
        # Verificar uso de recursos
        cpu_usage=$(docker stats cinemax_api --no-stream --format "{{.CPUPerc}}" | tr -d '%')
        if [ -n "$cpu_usage" ] && [ "$cpu_usage" -gt 90 ]; then
            log "🚨 CRÍTICO: Uso de CPU muy alto ($cpu_usage%)"
        elif [ -n "$cpu_usage" ] && [ "$cpu_usage" -gt 80 ]; then
            log "⚠️  ADVERTENCIA: Uso de CPU alto ($cpu_usage%)"
        fi
        
        memory_usage=$(docker stats cinemax_api --no-stream --format "{{.MemUsage}}" | cut -d'/' -f1 | tr -d 'MiB')
        if [ -n "$memory_usage" ] && [ "$memory_usage" -gt 1000 ]; then
            log "⚠️  ADVERTENCIA: Uso de memoria alto (${memory_usage}MB)"
        fi
        
        sleep $INTERVAL
    done
}

# Función para mostrar ayuda
show_help() {
    echo "📊 Script de Monitoreo del Sistema de Cine"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  dashboard     Mostrar dashboard en tiempo real"
    echo "  continuous    Monitoreo continuo con logs"
    echo "  alerts        Monitoreo con alertas"
    echo "  report        Generar reporte de métricas"
    echo "  help          Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 dashboard    # Dashboard en tiempo real"
    echo "  $0 continuous   # Monitoreo continuo"
    echo "  $0 alerts       # Monitoreo con alertas"
    echo "  $0 report       # Generar reporte"
}

# FUNCIÓN PRINCIPAL
main() {
    case "${1:-help}" in
        "dashboard")
            show_dashboard
            ;;
        "continuous")
            continuous_monitoring
            ;;
        "alerts")
            monitor_with_alerts
            ;;
        "report")
            generate_metrics_report
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Ejecutar función principal
main "$@" 