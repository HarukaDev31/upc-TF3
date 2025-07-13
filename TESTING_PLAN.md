# 🧪 Plan de Pruebas - Sistema de Cine

Este documento detalla todas las pruebas que puedes realizar en tu sistema de cine para evaluar funcionalidad, rendimiento y escalabilidad.

## 📋 Contenido

- [Tipos de Pruebas](#tipos-de-pruebas)
- [Pruebas Funcionales](#pruebas-funcionales)
- [Pruebas de Rendimiento](#pruebas-de-rendimiento)
- [Pruebas de Carga](#pruebas-de-carga)
- [Pruebas de Estrés](#pruebas-de-estrés)
- [Pruebas de Integración](#pruebas-de-integración)
- [Pruebas de Base de Datos](#pruebas-de-base-de-datos)
- [Pruebas de Cache](#pruebas-de-cache)
- [Herramientas de Pruebas](#herramientas-de-pruebas)
- [Scripts de Automatización](#scripts-de-automatización)

## 🎯 Tipos de Pruebas

### 1. **Pruebas Funcionales** ✅
- Verificar que cada endpoint funcione correctamente
- Validar respuestas y códigos de estado
- Probar casos de éxito y error

### 2. **Pruebas de Rendimiento** ⚡
- Medir tiempos de respuesta
- Evaluar throughput
- Analizar uso de recursos

### 3. **Pruebas de Carga** 📈
- Simular múltiples usuarios concurrentes
- Probar límites del sistema
- Identificar cuellos de botella

### 4. **Pruebas de Estrés** 🔥
- Llevar el sistema al límite
- Probar recuperación ante fallos
- Evaluar estabilidad

### 5. **Pruebas de Integración** 🔗
- Verificar comunicación entre servicios
- Probar Redis + MongoDB
- Validar flujos completos

## 🧪 Pruebas Funcionales

### Endpoints Básicos

```bash
# 1. Health Check
curl -X GET http://localhost:8000/health
# Esperado: 200 OK, servicios conectados

# 2. Bienvenida
curl -X GET http://localhost:8000/
# Esperado: 200 OK, información de la API
```

### Gestión de Películas

```bash
# 3. Listar Películas (paginación)
curl -X GET "http://localhost:8000/api/v1/peliculas?limite=10&offset=0"
# Esperado: 200 OK, lista de películas

# 4. Listar Películas (sin parámetros)
curl -X GET "http://localhost:8000/api/v1/peliculas"
# Esperado: 200 OK, lista con límite por defecto

# 5. Funciones de Película
curl -X GET "http://localhost:8000/api/v1/peliculas/pel_000001/funciones"
# Esperado: 200 OK, funciones de la película

# 6. Buscar Películas
curl -X POST http://localhost:8000/api/v1/buscar-peliculas \
  -H "Content-Type: application/json" \
  -d '{"texto": "accion", "genero": "accion", "limite": 20}'
# Esperado: 200 OK, películas filtradas
```

### Gestión de Funciones

```bash
# 7. Asientos de Función
curl -X GET "http://localhost:8000/api/v1/funciones/fun_000001/asientos"
# Esperado: 200 OK, mapa de asientos
```

### Compra de Entradas

```bash
# 8. Comprar Entrada (éxito)
curl -X POST http://localhost:8000/api/v1/comprar-entrada \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "cliente_000001",
    "pelicula_id": "pel_000001",
    "funcion_id": "fun_000001",
    "asientos": ["A5", "A6"],
    "metodo_pago": "tarjeta"
  }'
# Esperado: 200 OK, transacción creada

# 9. Comprar Entrada (asientos ocupados)
curl -X POST http://localhost:8000/api/v1/comprar-entrada \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "cliente_000002",
    "pelicula_id": "pel_000001",
    "funcion_id": "fun_000001",
    "asientos": ["A5", "A6"],
    "metodo_pago": "tarjeta"
  }'
# Esperado: 400 Bad Request, asientos ocupados
```

### Métricas y Analytics

```bash
# 10. Ranking de Películas
curl -X GET "http://localhost:8000/api/v1/metricas/ranking-peliculas?limite=10"
# Esperado: 200 OK, ranking de películas

# 11. Ocupación de Sala
curl -X GET "http://localhost:8000/api/v1/metricas/ocupacion/fun_000001"
# Esperado: 200 OK, estadísticas de ocupación
```

## ⚡ Pruebas de Rendimiento

### Medición de Tiempos de Respuesta

```bash
# Script para medir tiempos de respuesta
for i in {1..100}; do
    start=$(date +%s%N)
    curl -s -X GET "http://localhost:8000/api/v1/peliculas?limite=10" > /dev/null
    end=$(date +%s%N)
    echo "Request $i: $(( (end - start) / 1000000 ))ms"
done
```

### Pruebas de Throughput

```bash
# Usando Apache Bench (ab)
# 1000 requests, 10 concurrent users
ab -n 1000 -c 10 http://localhost:8000/api/v1/peliculas

# 100 requests, 50 concurrent users
ab -n 100 -c 50 http://localhost:8000/health
```

### Pruebas de Consultas de Base de Datos

```javascript
// MongoDB - Consultas de rendimiento
// 1. Búsqueda por género
db.peliculas.find({generos: "accion"}).explain("executionStats")

// 2. Funciones próximas
db.funciones.find({
    fecha_hora_inicio: {
        $gte: new Date(),
        $lte: new Date(Date.now() + 7*24*60*60*1000)
    }
}).explain("executionStats")

// 3. Clientes premium
db.clientes.find({tipo: "premium"}).explain("executionStats")
```

## 📈 Pruebas de Carga

### Escenarios de Carga

#### **Escenario 1: Carga Normal**
```bash
# 100 usuarios concurrentes, 1000 requests total
ab -n 1000 -c 100 http://localhost:8000/api/v1/peliculas
```

#### **Escenario 2: Pico de Tráfico**
```bash
# 500 usuarios concurrentes, 5000 requests total
ab -n 5000 -c 500 http://localhost:8000/api/v1/peliculas
```

#### **Escenario 3: Compra de Entradas**
```bash
# Simular múltiples compras simultáneas
for i in {1..100}; do
    curl -X POST http://localhost:8000/api/v1/comprar-entrada \
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
```

### Script de Pruebas de Carga

```bash
#!/bin/bash
# load_test.sh

echo "🚀 Iniciando pruebas de carga..."

# Configuración
BASE_URL="http://localhost:8000"
TOTAL_REQUESTS=1000
CONCURRENT_USERS=50

echo "📊 Configuración:"
echo "   - Total requests: $TOTAL_REQUESTS"
echo "   - Usuarios concurrentes: $CONCURRENT_USERS"
echo "   - URL base: $BASE_URL"
echo ""

# 1. Health Check
echo "🏥 Probando Health Check..."
ab -n 100 -c 10 "$BASE_URL/health"

# 2. Listar Películas
echo "🎬 Probando Listar Películas..."
ab -n $TOTAL_REQUESTS -c $CONCURRENT_USERS "$BASE_URL/api/v1/peliculas?limite=20"

# 3. Buscar Películas
echo "🔍 Probando Búsqueda de Películas..."
ab -n 500 -c 25 -p search_data.json -T application/json "$BASE_URL/api/v1/buscar-peliculas"

# 4. Comprar Entradas
echo "🎫 Probando Compra de Entradas..."
ab -n 200 -c 10 -p purchase_data.json -T application/json "$BASE_URL/api/v1/comprar-entrada"

echo "✅ Pruebas de carga completadas!"
```

## 🔥 Pruebas de Estrés

### Límites del Sistema

```bash
# 1. Máximo de conexiones concurrentes
ab -n 10000 -c 1000 http://localhost:8000/api/v1/peliculas

# 2. Requests muy rápidos
ab -n 5000 -c 500 -r http://localhost:8000/health

# 3. Datos grandes
curl -X POST http://localhost:8000/api/v1/buscar-peliculas \
  -H "Content-Type: application/json" \
  -d '{"texto": "'$(printf 'a%.0s' {1..10000})'", "limite": 1000}'
```

### Pruebas de Recuperación

```bash
# 1. Simular fallo de MongoDB
docker stop cinemax_mongodb
sleep 10
docker start cinemax_mongodb

# 2. Simular fallo de Redis
docker stop cinemax_redis
sleep 10
docker start cinemax_redis

# 3. Simular alta carga de CPU
docker exec cinemax_api stress-ng --cpu 4 --timeout 30s
```

## 🔗 Pruebas de Integración

### Flujo Completo de Compra

```bash
#!/bin/bash
# integration_test.sh

echo "🔗 Probando flujo completo de compra..."

# 1. Verificar salud del sistema
curl -s "$BASE_URL/health" | jq '.estado'

# 2. Listar películas
PELICULA_ID=$(curl -s "$BASE_URL/api/v1/peliculas?limite=1" | jq -r '.peliculas[0].id')

# 3. Obtener funciones de la película
FUNCION_ID=$(curl -s "$BASE_URL/api/v1/peliculas/$PELICULA_ID/funciones" | jq -r '.funciones[0].id')

# 4. Ver asientos disponibles
curl -s "$BASE_URL/api/v1/funciones/$FUNCION_ID/asientos" | jq '.asientos_disponibles'

# 5. Comprar entrada
TRANSACCION=$(curl -s -X POST "$BASE_URL/api/v1/comprar-entrada" \
  -H "Content-Type: application/json" \
  -d "{
    \"cliente_id\": \"cliente_000001\",
    \"pelicula_id\": \"$PELICULA_ID\",
    \"funcion_id\": \"$FUNCION_ID\",
    \"asientos\": [\"A5\"],
    \"metodo_pago\": \"tarjeta\"
  }")

echo "✅ Transacción completada: $TRANSACCION"
```

### Comunicación entre Servicios

```bash
# Verificar conexión Redis
docker exec cinemax_redis redis-cli ping

# Verificar conexión MongoDB
docker exec cinemax_mongodb mongosh --eval "db.adminCommand('ping')"

# Verificar métricas de Prometheus
curl -s http://localhost:9090/api/v1/query?query=up
```

## 🗄️ Pruebas de Base de Datos

### Consultas de Rendimiento

```javascript
// 1. Análisis de índices
db.peliculas.getIndexes()
db.funciones.getIndexes()
db.transacciones.getIndexes()

// 2. Estadísticas de colecciones
db.peliculas.stats()
db.funciones.stats()
db.transacciones.stats()

// 3. Consultas complejas
db.funciones.aggregate([
    {
        $match: {
            fecha_hora_inicio: {
                $gte: new Date(),
                $lte: new Date(Date.now() + 7*24*60*60*1000)
            }
        }
    },
    {
        $group: {
            _id: "$estado",
            count: {$sum: 1},
            avg_price: {$avg: "$precio_base"}
        }
    }
])

// 4. Pruebas de concurrencia
// Simular múltiples compras simultáneas
for (let i = 0; i < 100; i++) {
    db.transacciones.insertOne({
        cliente_id: "cliente_" + i,
        funcion_id: "fun_000001",
        asientos: ["A" + i],
        estado: "confirmada",
        fecha_creacion: new Date()
    });
}
```

## 🚀 Pruebas de Cache (Redis)

### Operaciones de Cache

```bash
# 1. Verificar conexión Redis
docker exec cinemax_redis redis-cli ping

# 2. Probar operaciones básicas
docker exec cinemax_redis redis-cli SET "test:key" "test:value"
docker exec cinemax_redis redis-cli GET "test:key"

# 3. Probar bitmaps (para asientos)
docker exec cinemax_redis redis-cli SETBIT "sala:asientos:fun_000001" 0 1
docker exec cinemax_redis redis-cli GETBIT "sala:asientos:fun_000001" 0

# 4. Probar sorted sets (para rankings)
docker exec cinemax_redis redis-cli ZADD "ranking:peliculas" 100 "pel_000001" 200 "pel_000002"
docker exec cinemax_redis redis-cli ZRANGE "ranking:peliculas" 0 -1 WITHSCORES
```

### Pruebas de Rendimiento de Cache

```bash
# 1. Benchmark de Redis
docker exec cinemax_redis redis-benchmark -n 10000 -c 50

# 2. Pruebas de memoria
docker exec cinemax_redis redis-cli INFO memory

# 3. Pruebas de persistencia
docker exec cinemax_redis redis-cli BGSAVE
docker exec cinemax_redis redis-cli LASTSAVE
```

## 🛠️ Herramientas de Pruebas

### Herramientas Recomendadas

1. **Apache Bench (ab)** - Pruebas de carga básicas
2. **wrk** - Pruebas de carga avanzadas
3. **Artillery** - Pruebas de carga con JavaScript
4. **JMeter** - Pruebas de carga GUI
5. **k6** - Pruebas de rendimiento modernas
6. **Postman** - Pruebas funcionales
7. **curl** - Pruebas rápidas de línea de comandos

### Instalación de Herramientas

```bash
# Apache Bench (ya incluido en muchos sistemas)
ab -V

# wrk
git clone https://github.com/wg/wrk.git
cd wrk && make

# Artillery
npm install -g artillery

# k6
# Descargar desde https://k6.io/docs/getting-started/installation/
```

## 🤖 Scripts de Automatización

### Script de Pruebas Automáticas

```bash
#!/bin/bash
# auto_test.sh

echo "🤖 Iniciando pruebas automáticas..."

# Configuración
BASE_URL="http://localhost:8000"
LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"

# Función para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 1. Pruebas de salud
log "🏥 Probando health check..."
if curl -s "$BASE_URL/health" | jq -e '.estado == "saludable"' > /dev/null; then
    log "✅ Health check exitoso"
else
    log "❌ Health check falló"
    exit 1
fi

# 2. Pruebas funcionales
log "🧪 Ejecutando pruebas funcionales..."
for endpoint in "/" "/api/v1/peliculas" "/api/v1/peliculas/pel_000001/funciones"; do
    if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" | grep -q "200"; then
        log "✅ $endpoint - OK"
    else
        log "❌ $endpoint - FALLÓ"
    fi
done

# 3. Pruebas de rendimiento
log "⚡ Ejecutando pruebas de rendimiento..."
ab -n 100 -c 10 "$BASE_URL/api/v1/peliculas" 2>&1 | tee -a "$LOG_FILE"

# 4. Pruebas de carga
log "📈 Ejecutando pruebas de carga..."
ab -n 1000 -c 50 "$BASE_URL/api/v1/peliculas" 2>&1 | tee -a "$LOG_FILE"

log "✅ Pruebas automáticas completadas!"
log "📁 Resultados guardados en: $LOG_FILE"
```

### Script de Monitoreo Continuo

```bash
#!/bin/bash
# monitor.sh

echo "📊 Iniciando monitoreo continuo..."

while true; do
    echo "=== $(date) ==="
    
    # Health check
    curl -s "$BASE_URL/health" | jq '.'
    
    # Métricas de Docker
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    # Métricas de MongoDB
    docker exec cinemax_mongodb mongosh --eval "db.stats()" --quiet
    
    # Métricas de Redis
    docker exec cinemax_redis redis-cli INFO memory
    
    sleep 30
done
```

## 📊 Métricas a Monitorear

### Métricas de Aplicación
- **Tiempo de respuesta** (p50, p95, p99)
- **Throughput** (requests/segundo)
- **Error rate** (% de errores)
- **Concurrent users** (usuarios simultáneos)

### Métricas de Infraestructura
- **CPU usage** (% de uso)
- **Memory usage** (uso de memoria)
- **Disk I/O** (operaciones de disco)
- **Network I/O** (tráfico de red)

### Métricas de Base de Datos
- **Query performance** (tiempo de consulta)
- **Index usage** (uso de índices)
- **Connection pool** (pool de conexiones)
- **Cache hit rate** (tasa de acierto de cache)

## 🎯 Checklist de Pruebas

### ✅ Pruebas Funcionales
- [ ] Health check responde correctamente
- [ ] Todos los endpoints devuelven códigos HTTP correctos
- [ ] Validación de datos de entrada funciona
- [ ] Manejo de errores es apropiado
- [ ] Respuestas JSON son válidas

### ✅ Pruebas de Rendimiento
- [ ] Tiempo de respuesta < 200ms para endpoints básicos
- [ ] Tiempo de respuesta < 1000ms para consultas complejas
- [ ] Throughput > 1000 requests/segundo
- [ ] Uso de memoria < 1GB
- [ ] CPU usage < 80% bajo carga

### ✅ Pruebas de Carga
- [ ] Sistema maneja 100 usuarios concurrentes
- [ ] Sistema maneja 1000 requests/segundo
- [ ] No hay memory leaks bajo carga
- [ ] Recuperación después de picos de tráfico
- [ ] Degradación graceful bajo estrés

### ✅ Pruebas de Integración
- [ ] Redis y MongoDB se comunican correctamente
- [ ] Flujos completos funcionan end-to-end
- [ ] Transacciones son atómicas
- [ ] Cache funciona correctamente
- [ ] Métricas se generan apropiadamente

---

**¡Tu sistema de cine está listo para pruebas exhaustivas! 🎬✨** 