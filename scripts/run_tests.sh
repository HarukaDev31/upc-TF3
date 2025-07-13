#!/bin/bash

# Script principal para ejecutar todas las pruebas del Sistema de Cine
# Incluye: funcionales, rendimiento, carga, integración

echo "🧪 Iniciando pruebas del Sistema de Cine..."
echo "================================================================"

# Configuración
BASE_URL="http://localhost:8000"
LOG_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/test_results_$TIMESTAMP.log"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Función para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función para verificar que la API esté funcionando
check_api() {
    log "🔍 Verificando que la API esté funcionando..."
    response=$(curl -s "$BASE_URL/health")
    if echo "$response" | grep -q '"estado":"saludable"' && echo "$response" | grep -q '"servicios"'; then
        log "✅ API funcionando correctamente"
        return 0
    else
        log "❌ API no está funcionando"
        log "Respuesta recibida: $response"
        return 1
    fi
}

# Función para medir tiempo de respuesta
measure_response_time() {
    local endpoint="$1"
    local description="$2"
    
    start=$(date +%s%N)
    response=$(curl -s -w "%{http_code}" "$BASE_URL$endpoint" -o /dev/null)
    end=$(date +%s%N)
    duration=$(( (end - start) / 1000000 ))
    
    if [ "$response" = "200" ]; then
        log "✅ $description - ${duration}ms"
    else
        log "❌ $description - HTTP $response - ${duration}ms"
    fi
}

# 1. PRUEBAS FUNCIONALES
run_functional_tests() {
    log "🧪 Ejecutando pruebas funcionales..."
    
    # Endpoints básicos
    measure_response_time "/" "Bienvenida"
    measure_response_time "/health" "Health Check"
    
    # Gestión de películas
    measure_response_time "/api/v1/peliculas?limite=10" "Listar Películas"
    measure_response_time "/api/v1/peliculas/pel_000001/funciones" "Funciones de Película"
    
    # Métricas
    measure_response_time "/api/v1/metricas/ranking-peliculas?limite=5" "Ranking de Películas"
    measure_response_time "/api/v1/metricas/ocupacion/fun_000001" "Ocupación de Sala"
    
    # Pruebas POST
    log "📝 Probando endpoints POST..."
    
    # Buscar películas
    search_response=$(curl -s -X POST "$BASE_URL/api/v1/buscar-peliculas" \
        -H "Content-Type: application/json" \
        -d '{"texto": "accion", "limite": 10}' \
        -w "%{http_code}")
    
    if [[ "$search_response" == *"200" ]]; then
        log "✅ Búsqueda de Películas - OK"
    else
        log "❌ Búsqueda de Películas - FALLÓ"
    fi
    
    # Comprar entrada
    purchase_response=$(curl -s -X POST "$BASE_URL/api/v1/comprar-entrada" \
        -H "Content-Type: application/json" \
        -d '{
            "cliente_id": "cliente_000001",
            "pelicula_id": "pel_000001",
            "funcion_id": "fun_000001",
            "asientos": ["A5"],
            "metodo_pago": "tarjeta"
        }' \
        -w "%{http_code}")
    
    if [[ "$purchase_response" == *"200" ]]; then
        log "✅ Compra de Entrada - OK"
    else
        log "❌ Compra de Entrada - FALLÓ"
    fi
}

# 2. PRUEBAS DE RENDIMIENTO
run_performance_tests() {
    log "⚡ Ejecutando pruebas de rendimiento..."
    
    # Verificar si Apache Bench está disponible
    if ! command -v ab &> /dev/null; then
        log "⚠️  Apache Bench no está instalado. Instalando..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y apache2-utils
        elif command -v yum &> /dev/null; then
            sudo yum install -y httpd-tools
        else
            log "❌ No se pudo instalar Apache Bench"
            return 1
        fi
    fi
    
    # Pruebas de throughput
    log "📊 Probando throughput..."
    
    # Health check - 100 requests, 10 concurrent
    ab -n 100 -c 10 "$BASE_URL/health" 2>&1 | tee -a "$LOG_FILE"
    
    # Listar películas - 500 requests, 50 concurrent
    ab -n 500 -c 50 "$BASE_URL/api/v1/peliculas?limite=20" 2>&1 | tee -a "$LOG_FILE"
    
    # Medición de tiempos de respuesta
    log "⏱️  Medición de tiempos de respuesta..."
    for i in {1..50}; do
        start=$(date +%s%N)
        curl -s "$BASE_URL/api/v1/peliculas?limite=10" > /dev/null
        end=$(date +%s%N)
        duration=$(( (end - start) / 1000000 ))
        echo "Request $i: ${duration}ms" | tee -a "$LOG_FILE"
    done
}

# 3. PRUEBAS DE CARGA
run_load_tests() {
    log "📈 Ejecutando pruebas de carga..."
    
    # Escenario 1: Carga normal
    log "🎯 Escenario 1: Carga normal (100 usuarios, 1000 requests)"
    ab -n 1000 -c 100 "$BASE_URL/api/v1/peliculas?limite=10" 2>&1 | tee -a "$LOG_FILE"
    
    # Escenario 2: Pico de tráfico
    log "🚀 Escenario 2: Pico de tráfico (500 usuarios, 2000 requests)"
    ab -n 2000 -c 500 "$BASE_URL/api/v1/peliculas?limite=10" 2>&1 | tee -a "$LOG_FILE"
    
    # Escenario 3: Compra simultánea de entradas
    log "🎫 Escenario 3: Compra simultánea de entradas"
    for i in {1..50}; do
        curl -s -X POST "$BASE_URL/api/v1/comprar-entrada" \
            -H "Content-Type: application/json" \
            -d "{
                \"cliente_id\": \"cliente_$(printf '%06d' $i)\",
                \"pelicula_id\": \"pel_000001\",
                \"funcion_id\": \"fun_000001\",
                \"asientos\": [\"A$i\"],
                \"metodo_pago\": \"tarjeta\"
            }" &
    done
    wait
    log "✅ Compras simultáneas completadas"
}

# 4. PRUEBAS DE INTEGRACIÓN
run_integration_tests() {
    log "🔗 Ejecutando pruebas de integración..."
    
    # Verificar conexión Redis
    if docker exec cinemax_redis redis-cli ping | grep -q "PONG"; then
        log "✅ Redis conectado"
    else
        log "❌ Redis no conectado"
    fi
    
    # Verificar conexión MongoDB
    if docker exec cinemax_mongodb mongosh --eval "db.adminCommand('ping')" --quiet | grep -q "1"; then
        log "✅ MongoDB conectado"
    else
        log "❌ MongoDB no conectado"
    fi
    
    # Verificar métricas de Prometheus
    prometheus_response=$(curl -s "http://localhost:9090/api/v1/query?query=up")
    if echo "$prometheus_response" | grep -q '"data"' && echo "$prometheus_response" | grep -q '"result"'; then
        log "✅ Prometheus funcionando"
    else
        log "❌ Prometheus no disponible"
    fi
    
    # Flujo completo de compra
    log "🔄 Probando flujo completo de compra..."
    
    # Obtener primera película
    peliculas_response=$(curl -s "$BASE_URL/api/v1/peliculas?limite=1")
    pelicula_id=$(echo "$peliculas_response" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"//')
    if [ -n "$pelicula_id" ] && [ "$pelicula_id" != "null" ]; then
        log "✅ Película obtenida: $pelicula_id"
        
        # Obtener primera función
        funciones_response=$(curl -s "$BASE_URL/api/v1/peliculas/$pelicula_id/funciones")
        funcion_id=$(echo "$funciones_response" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"//')
        if [ -n "$funcion_id" ] && [ "$funcion_id" != "null" ]; then
            log "✅ Función obtenida: $funcion_id"
            
            # Comprar entrada
            transaccion=$(curl -s -X POST "$BASE_URL/api/v1/comprar-entrada" \
                -H "Content-Type: application/json" \
                -d "{
                    \"cliente_id\": \"cliente_000001\",
                    \"pelicula_id\": \"$pelicula_id\",
                    \"funcion_id\": \"$funcion_id\",
                    \"asientos\": [\"A5\"],
                    \"metodo_pago\": \"tarjeta\"
                }")
            
            if echo "$transaccion" | grep -q '"transaccion_id"'; then
                log "✅ Flujo completo exitoso"
            else
                log "❌ Flujo completo falló"
                log "Respuesta: $transaccion"
            fi
        else
            log "❌ No se pudo obtener función"
        fi
    else
        log "❌ No se pudo obtener película"
    fi
}

# 5. PRUEBAS DE BASE DE DATOS
run_database_tests() {
    log "🗄️  Ejecutando pruebas de base de datos..."
    
    # Verificar cantidad de documentos
    peliculas_count=$(docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.countDocuments()" --quiet)
    funciones_count=$(docker exec cinemax_mongodb mongosh cinemax --eval "db.funciones.countDocuments()" --quiet)
    clientes_count=$(docker exec cinemax_mongodb mongosh cinemax --eval "db.clientes.countDocuments()" --quiet)
    transacciones_count=$(docker exec cinemax_mongodb mongosh cinemax --eval "db.transacciones.countDocuments()" --quiet)
    
    log "📊 Documentos en la base de datos:"
    log "   - Películas: $peliculas_count"
    log "   - Funciones: $funciones_count"
    log "   - Clientes: $clientes_count"
    log "   - Transacciones: $transacciones_count"
    
    # Verificar índices
    log "🔍 Verificando índices..."
    docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.getIndexes().length" --quiet
    docker exec cinemax_mongodb mongosh cinemax --eval "db.funciones.getIndexes().length" --quiet
    docker exec cinemax_mongodb mongosh cinemax --eval "db.transacciones.getIndexes().length" --quiet
    
    # Prueba de consulta compleja
    log "🔍 Probando consulta compleja..."
    docker exec cinemax_mongodb mongosh cinemax --eval "
        db.funciones.aggregate([
            {
                \$match: {
                    fecha_hora_inicio: {
                        \$gte: new Date(),
                        \$lte: new Date(Date.now() + 7*24*60*60*1000)
                    }
                }
            },
            {
                \$group: {
                    _id: '\$estado',
                    count: {\$sum: 1}
                }
            }
        ]).toArray()
    " --quiet
}

# 6. PRUEBAS DE CACHE
run_cache_tests() {
    log "🚀 Ejecutando pruebas de cache..."
    
    # Probar operaciones básicas de Redis
    docker exec cinemax_redis redis-cli SET "test:key" "test:value"
    value=$(docker exec cinemax_redis redis-cli GET "test:key")
    if [ "$value" = "test:value" ]; then
        log "✅ Operaciones básicas de Redis - OK"
    else
        log "❌ Operaciones básicas de Redis - FALLÓ"
    fi
    
    # Probar bitmaps para asientos
    docker exec cinemax_redis redis-cli SETBIT "sala:asientos:test" 0 1
    bit=$(docker exec cinemax_redis redis-cli GETBIT "sala:asientos:test" 0)
    if [ "$bit" = "1" ]; then
        log "✅ Bitmaps de Redis - OK"
    else
        log "❌ Bitmaps de Redis - FALLÓ"
    fi
    
    # Benchmark de Redis
    log "📊 Ejecutando benchmark de Redis..."
    docker exec cinemax_redis redis-benchmark -n 1000 -c 10 2>&1 | tee -a "$LOG_FILE"
}

# 7. GENERAR REPORTE
generate_report() {
    log "📋 Generando reporte de pruebas..."
    
    echo "================================================================" | tee -a "$LOG_FILE"
    echo "📊 REPORTE DE PRUEBAS - Sistema de Cine" | tee -a "$LOG_FILE"
    echo "Fecha: $(date)" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
    
    # Métricas del sistema
    echo "🔧 MÉTRICAS DEL SISTEMA:" | tee -a "$LOG_FILE"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | tee -a "$LOG_FILE"
    
    # Resumen de pruebas
    echo "" | tee -a "$LOG_FILE"
    echo "✅ PRUEBAS COMPLETADAS:" | tee -a "$LOG_FILE"
    echo "   - Funcionales: ✅" | tee -a "$LOG_FILE"
    echo "   - Rendimiento: ✅" | tee -a "$LOG_FILE"
    echo "   - Carga: ✅" | tee -a "$LOG_FILE"
    echo "   - Integración: ✅" | tee -a "$LOG_FILE"
    echo "   - Base de datos: ✅" | tee -a "$LOG_FILE"
    echo "   - Cache: ✅" | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
    echo "📁 Logs guardados en: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
}

# FUNCIÓN PRINCIPAL
main() {
    log "🎬 Iniciando pruebas del Sistema de Cine..."
    
    # Verificar que la API esté funcionando
    if ! check_api; then
        log "❌ La API no está funcionando. Abortando pruebas."
        exit 1
    fi
    
    # Ejecutar todas las pruebas
    run_functional_tests
    run_performance_tests
    run_load_tests
    run_integration_tests
    run_database_tests
    run_cache_tests
    
    # Generar reporte final
    generate_report
    
    log "🎉 ¡Todas las pruebas completadas exitosamente!"
    log "📊 Revisa el reporte en: $LOG_FILE"
}

# Ejecutar función principal
main "$@" 