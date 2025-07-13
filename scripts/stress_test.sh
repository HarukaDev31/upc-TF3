#!/bin/bash

# Script de pruebas de estrés para el Sistema de Cine
# Evalúa el comportamiento del sistema bajo condiciones extremas

echo "🔥 Iniciando pruebas de estrés del Sistema de Cine..."
echo "================================================================"

# Configuración
BASE_URL="http://localhost:8000"
LOG_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/stress_test_$TIMESTAMP.log"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Función para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función para verificar que la API esté funcionando
check_api() {
    response=$(curl -s "$BASE_URL/health")
    if echo "$response" | grep -q '"estado":"saludable"' && echo "$response" | grep -q '"servicios"'; then
        return 0
    else
        return 1
    fi
}

# 1. PRUEBA DE ESTRÉS - MÁXIMAS CONEXIONES CONCURRENTES
test_max_concurrent_connections() {
    log "🔥 Prueba 1: Máximas conexiones concurrentes"
    
    # Probar con diferentes niveles de concurrencia
    for concurrent in 100 500 1000 2000; do
        log "📊 Probando con $concurrent usuarios concurrentes..."
        
        # Usar Apache Bench para probar límites
        ab -n 1000 -c $concurrent "$BASE_URL/api/v1/peliculas?limite=10" 2>&1 | tee -a "$LOG_FILE"
        
        # Verificar si la API sigue respondiendo
        if check_api; then
            log "✅ API sigue funcionando con $concurrent usuarios concurrentes"
        else
            log "❌ API falló con $concurrent usuarios concurrentes"
            break
        fi
        
        sleep 5
    done
}

# 2. PRUEBA DE ESTRÉS - REQUESTS MUY RÁPIDOS
test_rapid_requests() {
    log "⚡ Prueba 2: Requests muy rápidos"
    
    # Probar requests sin esperar respuesta
    for i in {1..1000}; do
        curl -s "$BASE_URL/api/v1/peliculas?limite=1" > /dev/null &
        
        # Cada 100 requests, verificar si la API sigue funcionando
        if [ $((i % 100)) -eq 0 ]; then
            if check_api; then
                log "✅ API funcionando después de $i requests rápidos"
            else
                log "❌ API falló después de $i requests rápidos"
                break
            fi
        fi
    done
    
    wait
    log "✅ Requests rápidos completados"
}

# 3. PRUEBA DE ESTRÉS - DATOS GRANDES
test_large_data() {
    log "📦 Prueba 3: Datos grandes"
    
    # Generar datos grandes para enviar
    large_text=$(printf 'a%.0s' {1..10000})
    
    # Probar búsqueda con datos grandes
    for i in {1..50}; do
        curl -s -X POST "$BASE_URL/api/v1/buscar-peliculas" \
            -H "Content-Type: application/json" \
            -d "{\"texto\": \"$large_text\", \"limite\": 1000}" > /dev/null &
    done
    
    wait
    log "✅ Pruebas de datos grandes completadas"
}

# 4. PRUEBA DE ESTRÉS - COMPRAS SIMULTÁNEAS
test_concurrent_purchases() {
    log "🎫 Prueba 4: Compras simultáneas"
    
    # Simular múltiples compras de los mismos asientos
    for i in {1..100}; do
        curl -s -X POST "$BASE_URL/api/v1/comprar-entrada" \
            -H "Content-Type: application/json" \
            -d "{
                \"cliente_id\": \"cliente_$(printf '%06d' $i)\",
                \"pelicula_id\": \"pel_000001\",
                \"funcion_id\": \"fun_000001\",
                \"asientos\": [\"A1\"],
                \"metodo_pago\": \"tarjeta\"
            }" &
    done
    
    wait
    log "✅ Compras simultáneas completadas"
}

# 5. PRUEBA DE ESTRÉS - FALLO DE SERVICIOS
test_service_failure() {
    log "💥 Prueba 5: Simulación de fallos de servicios"
    
    # Simular fallo de MongoDB
    log "🔄 Simulando fallo de MongoDB..."
    docker stop cinemax_mongodb
    sleep 10
    
    # Verificar comportamiento de la API
    if check_api; then
        log "✅ API maneja fallo de MongoDB correctamente"
    else
        log "❌ API no maneja fallo de MongoDB"
    fi
    
    # Restaurar MongoDB
    docker start cinemax_mongodb
    sleep 15
    
    # Verificar recuperación
    if check_api; then
        log "✅ API se recuperó después del fallo de MongoDB"
    else
        log "❌ API no se recuperó después del fallo de MongoDB"
    fi
    
    # Simular fallo de Redis
    log "🔄 Simulando fallo de Redis..."
    docker stop cinemax_redis
    sleep 10
    
    # Verificar comportamiento de la API
    if check_api; then
        log "✅ API maneja fallo de Redis correctamente"
    else
        log "❌ API no maneja fallo de Redis"
    fi
    
    # Restaurar Redis
    docker start cinemax_redis
    sleep 15
    
    # Verificar recuperación
    if check_api; then
        log "✅ API se recuperó después del fallo de Redis"
    else
        log "❌ API no se recuperó después del fallo de Redis"
    fi
}

# 6. PRUEBA DE ESTRÉS - ALTA CARGA DE CPU
test_cpu_stress() {
    log "🔥 Prueba 6: Alta carga de CPU"
    
    # Verificar si stress-ng está disponible
    if ! docker exec cinemax_api which stress-ng > /dev/null 2>&1; then
        log "⚠️  Instalando stress-ng..."
        docker exec cinemax_api apt-get update && docker exec cinemax_api apt-get install -y stress-ng
    fi
    
    # Generar alta carga de CPU
    log "🔥 Generando alta carga de CPU..."
    docker exec cinemax_api stress-ng --cpu 4 --timeout 30s &
    stress_pid=$!
    
    # Probar la API durante la alta carga
    for i in {1..100}; do
        start=$(date +%s%N)
        curl -s "$BASE_URL/api/v1/peliculas?limite=10" > /dev/null
        end=$(date +%s%N)
        duration=$(( (end - start) / 1000000 ))
        
        if [ $duration -gt 5000 ]; then
            log "⚠️  Tiempo de respuesta lento: ${duration}ms"
        fi
        
        if [ $i -eq 50 ]; then
            log "📊 Mitad de pruebas completadas bajo alta carga de CPU"
        fi
    done
    
    # Esperar que termine stress-ng
    wait $stress_pid
    log "✅ Pruebas de alta carga de CPU completadas"
}

# 7. PRUEBA DE ESTRÉS - MEMORIA
test_memory_stress() {
    log "💾 Prueba 7: Estrés de memoria"
    
    # Generar alta carga de memoria
    log "💾 Generando alta carga de memoria..."
    docker exec cinemax_api stress-ng --vm 2 --vm-bytes 1G --timeout 30s &
    stress_pid=$!
    
    # Probar la API durante la alta carga de memoria
    for i in {1..50}; do
        curl -s "$BASE_URL/api/v1/peliculas?limite=100" > /dev/null
        
        if [ $((i % 10)) -eq 0 ]; then
            # Verificar uso de memoria
            memory_usage=$(docker stats cinemax_api --no-stream --format "{{.MemUsage}}" | cut -d'/' -f1)
            log "📊 Uso de memoria: $memory_usage"
        fi
    done
    
    # Esperar que termine stress-ng
    wait $stress_pid
    log "✅ Pruebas de estrés de memoria completadas"
}

# 8. PRUEBA DE ESTRÉS - RED
test_network_stress() {
    log "🌐 Prueba 8: Estrés de red"
    
    # Simular múltiples conexiones simultáneas
    log "🌐 Simulando múltiples conexiones simultáneas..."
    
    # Usar netcat para crear muchas conexiones
    for i in {1..100}; do
        (echo -e "GET /health HTTP/1.1\r\nHost: localhost:8000\r\n\r\n" | nc localhost 8000) &
    done
    
    wait
    log "✅ Pruebas de estrés de red completadas"
}

# 9. PRUEBA DE ESTRÉS - BASE DE DATOS
test_database_stress() {
    log "🗄️  Prueba 9: Estrés de base de datos"
    
    # Ejecutar consultas complejas simultáneamente
    log "🗄️  Ejecutando consultas complejas simultáneamente..."
    
    for i in {1..50}; do
        docker exec cinemax_mongodb mongosh cinemax --eval "
            db.funciones.aggregate([
                {
                    \$match: {
                        fecha_hora_inicio: {
                            \$gte: new Date(),
                            \$lte: new Date(Date.now() + 30*24*60*60*1000)
                        }
                    }
                },
                {
                    \$group: {
                        _id: '\$estado',
                        count: {\$sum: 1},
                        avg_price: {\$avg: '\$precio_base'}
                    }
                }
            ]).toArray()
        " --quiet &
    done
    
    wait
    log "✅ Pruebas de estrés de base de datos completadas"
}

# 10. PRUEBA DE ESTRÉS - CACHE
test_cache_stress() {
    log "🚀 Prueba 10: Estrés de cache"
    
    # Probar operaciones intensivas de Redis
    log "🚀 Ejecutando operaciones intensivas de Redis..."
    
    # Probar múltiples operaciones simultáneas
    for i in {1..1000}; do
        docker exec cinemax_redis redis-cli SET "stress:key:$i" "value:$i" &
        docker exec cinemax_redis redis-cli GET "stress:key:$i" &
        
        if [ $((i % 100)) -eq 0 ]; then
            log "📊 Operaciones de cache: $i"
        fi
    done
    
    wait
    log "✅ Pruebas de estrés de cache completadas"
}

# 11. GENERAR REPORTE DE ESTRÉS
generate_stress_report() {
    log "📋 Generando reporte de pruebas de estrés..."
    
    echo "================================================================" | tee -a "$LOG_FILE"
    echo "🔥 REPORTE DE PRUEBAS DE ESTRÉS - Sistema de Cine" | tee -a "$LOG_FILE"
    echo "Fecha: $(date)" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
    
    # Métricas del sistema después del estrés
    echo "🔧 MÉTRICAS DEL SISTEMA DESPUÉS DEL ESTRÉS:" | tee -a "$LOG_FILE"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | tee -a "$LOG_FILE"
    
    # Verificar estado final de la API
    if check_api; then
        echo "✅ API funcionando correctamente después de todas las pruebas de estrés" | tee -a "$LOG_FILE"
    else
        echo "❌ API no está funcionando después de las pruebas de estrés" | tee -a "$LOG_FILE"
    fi
    
    # Estadísticas de la base de datos
    echo "" | tee -a "$LOG_FILE"
    echo "📊 ESTADÍSTICAS DE LA BASE DE DATOS:" | tee -a "$LOG_FILE"
    docker exec cinemax_mongodb mongosh cinemax --eval "db.stats()" --quiet | tee -a "$LOG_FILE"
    
    # Estadísticas de Redis
    echo "" | tee -a "$LOG_FILE"
    echo "🚀 ESTADÍSTICAS DE REDIS:" | tee -a "$LOG_FILE"
    docker exec cinemax_redis redis-cli INFO memory | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
    echo "📁 Logs guardados en: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
}

# FUNCIÓN PRINCIPAL
main() {
    log "🔥 Iniciando pruebas de estrés del Sistema de Cine..."
    
    # Verificar que la API esté funcionando antes de empezar
    if ! check_api; then
        log "❌ La API no está funcionando. Abortando pruebas de estrés."
        exit 1
    fi
    
    # Ejecutar todas las pruebas de estrés
    test_max_concurrent_connections
    test_rapid_requests
    test_large_data
    test_concurrent_purchases
    test_service_failure
    test_cpu_stress
    test_memory_stress
    test_network_stress
    test_database_stress
    test_cache_stress
    
    # Generar reporte final
    generate_stress_report
    
    log "🎉 ¡Todas las pruebas de estrés completadas!"
    log "📊 Revisa el reporte en: $LOG_FILE"
}

# Ejecutar función principal
main "$@" 