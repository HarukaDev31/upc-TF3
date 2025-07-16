# 🐳 Servicios de Docker en Cinemax API - Explicación Detallada

## 📋 Visión General

El proyecto Cinemax API utiliza **6 servicios de Docker** que trabajan en conjunto para crear un sistema distribuido completo y escalable. Cada servicio tiene un propósito específico y contribuye al funcionamiento general de la aplicación.

---

## 🗄️ 1. MongoDB Database (`mongodb`)

### **¿Qué es?**
Base de datos NoSQL distribuida que almacena todos los datos persistentes del sistema.

### **Configuración:**
```yaml
mongodb:
  image: mongo:7.0
  container_name: cinemax_mongodb
  ports:
    - "27017:27017"
  environment:
    MONGO_INITDB_ROOT_USERNAME: admin
    MONGO_INITDB_ROOT_PASSWORD: password123
    MONGO_INITDB_DATABASE: cinemax
```

### **¿Para qué lo usamos?**
- **Almacenamiento de datos**: Películas, funciones, transacciones, usuarios
- **Persistencia**: Datos que deben sobrevivir reinicios del sistema
- **Escalabilidad**: Puede manejar grandes volúmenes de datos
- **Flexibilidad**: Esquema flexible para diferentes tipos de datos

### **Datos que almacena:**
```javascript
// Colección: peliculas
{
  "_id": ObjectId("..."),
  "titulo": "Avengers: Endgame",
  "rating": 9.0,
  "genero": "Acción",
  "duracion": 181,
  "precio": 12,
  "activa": true
}

// Colección: transacciones
{
  "_id": ObjectId("..."),
  "usuario_id": "user_123",
  "pelicula_id": "pel_456",
  "funcion_id": "func_789",
  "asientos": ["A1", "A2"],
  "total": 24,
  "fecha": ISODate("2024-01-15T19:00:00Z")
}
```

### **Ventajas en nuestro proyecto:**
- ✅ **Almacenamiento de algoritmos**: Guarda resultados de cálculos complejos
- ✅ **Historial de transacciones**: Mantiene registro completo de compras
- ✅ **Datos de usuarios**: Información de autenticación y preferencias
- ✅ **Métricas de rendimiento**: Logs de algoritmos y tiempos de respuesta

---

## 🔄 2. Redis Cache (`redis`)

### **¿Qué es?**
Sistema de cache en memoria que proporciona acceso ultra-rápido a datos frecuentemente utilizados.

### **Configuración:**
```yaml
redis:
  image: redis:7.2-alpine
  container_name: cinemax_redis
  ports:
    - "6380:6379"
  command: redis-server --appendonly yes --requirepass redis123
```

### **¿Para qué lo usamos?**
- **Cache de algoritmos**: Resultados de cálculos recursivos y ordenamientos
- **Sesiones de usuario**: Tokens JWT y datos de sesión
- **Colas de procesamiento**: Emails y notificaciones en background
- **Datos temporales**: Información que no necesita persistencia completa

### **Casos de uso específicos:**
```python
# Cache de películas populares
redis.set("peliculas_populares", json.dumps(peliculas), ex=3600)

# Cache de resultados de algoritmos
redis.set(f"quicksort_{hash_datos}", resultado_ordenado, ex=1800)

# Cola de emails
redis.lpush("email_queue", json.dumps(email_data))

# Sesiones de usuario
redis.set(f"session_{user_id}", session_data, ex=1800)
```

### **Ventajas en nuestro proyecto:**
- ✅ **Rendimiento**: Respuestas en < 50ms para datos cacheados
- ✅ **Reducción de carga**: Menos consultas a MongoDB
- ✅ **Procesamiento asíncrono**: Colas para emails y notificaciones
- ✅ **Optimización de algoritmos**: Cache de resultados computacionales

---

## 🚀 3. FastAPI Application (`api`)

### **¿Qué es?**
El servidor principal de la aplicación que contiene toda la lógica de negocio y algoritmos.

### **Configuración:**
```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: cinemax_api
  ports:
    - "8000:8000"
  environment:
    - MONGODB_URL=mongodb://admin:password123@mongodb:27017/cinemax
    - REDIS_HOST=redis
    - REDIS_PORT=6379
```

### **¿Para qué lo usamos?**
- **API REST**: Endpoints para todas las operaciones del cine
- **Algoritmos**: Implementación de recursividad, ordenamiento y búsqueda
- **Autenticación**: Manejo de JWT y sesiones
- **WebSockets**: Comunicación en tiempo real
- **Procesamiento de emails**: Generación y envío de QR

### **Funcionalidades principales:**
```python
# Endpoints de algoritmos
@app.post("/api/v1/algoritmos/recursivos/factorial")
async def factorial_recursivo(n: int):
    return algorithms_service.calcular_factorial_recursivo(n)

# Integración en flujo real
@app.get("/api/v1/peliculas")
async def obtener_peliculas(ordenar_por: str = None, algoritmo: str = None):
    peliculas = await get_peliculas_from_db()
    if ordenar_por and algoritmo:
        peliculas = algorithms_service.ordenar_peliculas(peliculas, algoritmo)
    return peliculas
```

### **Ventajas en nuestro proyecto:**
- ✅ **Integración transparente**: Algoritmos se ejecutan automáticamente
- ✅ **Rendimiento optimizado**: Respuestas rápidas con cache
- ✅ **Escalabilidad**: Puede manejar múltiples instancias
- ✅ **Documentación automática**: Swagger/OpenAPI integrado

---

## 🖥️ 4. MongoDB Express (`mongo-express`)

### **¿Qué es?**
Interfaz web para administrar y visualizar la base de datos MongoDB.

### **Configuración:**
```yaml
mongo-express:
  image: mongo-express:1.0.0
  container_name: cinemax_mongo_express
  ports:
    - "8081:8081"
  environment:
    ME_CONFIG_MONGODB_ADMINUSERNAME: admin
    ME_CONFIG_MONGODB_ADMINPASSWORD: password123
```

### **¿Para qué lo usamos?**
- **Administración visual**: Ver y editar datos directamente
- **Debugging**: Inspeccionar datos durante desarrollo
- **Monitoreo**: Ver el estado de las colecciones
- **Backup**: Exportar datos manualmente

### **Acceso:**
- **URL**: `http://localhost:8081`
- **Usuario**: `admin`
- **Contraseña**: `admin123`

### **Ventajas en nuestro proyecto:**
- ✅ **Desarrollo**: Debugging rápido de datos
- ✅ **Monitoreo**: Ver estado de algoritmos y transacciones
- ✅ **Mantenimiento**: Administración manual cuando sea necesario
- ✅ **Documentación**: Visualizar estructura de datos

---

## 🔍 5. Redis Commander (`redis-commander`)

### **¿Qué es?**
Interfaz web para administrar y visualizar el cache Redis.

### **Configuración:**
```yaml
redis-commander:
  image: rediscommander/redis-commander:latest
  container_name: cinemax_redis_commander
  ports:
    - "8082:8081"
  environment:
    - REDIS_HOSTS=local:redis:6379:0:redis123
```

### **¿Para qué lo usamos?**
- **Monitoreo de cache**: Ver qué datos están en memoria
- **Debugging**: Inspeccionar colas y sesiones
- **Optimización**: Analizar patrones de uso del cache
- **Administración**: Limpiar cache manualmente

### **Acceso:**
- **URL**: `http://localhost:8082`
- **Usuario**: `admin`
- **Contraseña**: `admin123`

### **Ventajas en nuestro proyecto:**
- ✅ **Monitoreo**: Ver rendimiento de algoritmos cacheados
- ✅ **Debugging**: Inspeccionar colas de emails
- ✅ **Optimización**: Analizar hit/miss ratio del cache
- ✅ **Mantenimiento**: Limpiar cache cuando sea necesario

---

## 📊 6. Prometheus (`prometheus`)

### **¿Qué es?**
Sistema de monitoreo y alertas que recolecta métricas de todos los servicios.

### **Configuración:**
```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: cinemax_prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

### **¿Para qué lo usamos?**
- **Métricas de algoritmos**: Tiempo de ejecución de cada algoritmo
- **Rendimiento de API**: Latencia y throughput
- **Uso de recursos**: CPU, memoria, disco
- **Alertas**: Notificaciones cuando algo falla

### **Métricas que recolecta:**
```yaml
# Métricas de algoritmos
algoritmo_tiempo_ejecucion{algoritmo="quicksort"} 0.045
algoritmo_tiempo_ejecucion{algoritmo="busqueda_binaria"} 0.002

# Métricas de API
http_requests_total{endpoint="/api/v1/peliculas"} 1250
http_request_duration_seconds{endpoint="/api/v1/peliculas"} 0.15
```

### **Ventajas en nuestro proyecto:**
- ✅ **Optimización**: Identificar algoritmos lentos
- ✅ **Escalabilidad**: Monitorear uso de recursos
- ✅ **Alertas**: Detectar problemas antes de que afecten usuarios
- ✅ **Análisis**: Tendencias de uso y rendimiento

---

## 📈 7. Grafana (`grafana`)

### **¿Qué es?**
Plataforma de visualización y dashboards para analizar métricas de Prometheus.

### **Configuración:**
```yaml
grafana:
  image: grafana/grafana:latest
  container_name: cinemax_grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin123
```

### **¿Para qué lo usamos?**
- **Dashboards**: Visualizar métricas en tiempo real
- **Análisis**: Tendencias de rendimiento de algoritmos
- **Alertas**: Configurar notificaciones automáticas
- **Reportes**: Generar informes de rendimiento

### **Dashboards disponibles:**
- **Rendimiento de Algoritmos**: Tiempo de ejecución por algoritmo
- **Métricas de API**: Requests, latencia, errores
- **Uso de Recursos**: CPU, memoria, disco
- **Cache Performance**: Hit/miss ratio de Redis

### **Acceso:**
- **URL**: `http://localhost:3000`
- **Usuario**: `admin`
- **Contraseña**: `admin123`

### **Ventajas en nuestro proyecto:**
- ✅ **Visualización**: Ver rendimiento de algoritmos en gráficos
- ✅ **Análisis**: Identificar cuellos de botella
- ✅ **Alertas**: Notificaciones automáticas de problemas
- ✅ **Reportes**: Documentar rendimiento del sistema

---

## 🔗 Interacción entre Servicios

### **Flujo de Datos:**
```
Cliente → FastAPI → Redis (Cache) → MongoDB (Persistencia)
                ↓
            Prometheus (Métricas) → Grafana (Visualización)
```

### **Comunicación:**
- **FastAPI ↔ MongoDB**: Consultas y escrituras de datos
- **FastAPI ↔ Redis**: Cache y colas de procesamiento
- **Prometheus → FastAPI**: Recolección de métricas
- **Grafana → Prometheus**: Consulta de métricas para dashboards

### **Dependencias:**
```yaml
api:
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy

mongo-express:
  depends_on:
    mongodb:
      condition: service_healthy

redis-commander:
  depends_on:
    redis:
      condition: service_healthy

grafana:
  depends_on:
    - prometheus
```

---

## 🎯 Beneficios del Sistema Distribuido

### **1. Escalabilidad**
- ✅ **MongoDB**: Puede escalar horizontalmente con réplicas
- ✅ **Redis**: Cluster para cache distribuido
- ✅ **FastAPI**: Múltiples instancias detrás de load balancer

### **2. Resiliencia**
- ✅ **Health checks**: Monitoreo automático de servicios
- ✅ **Restart policies**: Recuperación automática
- ✅ **Volumes**: Persistencia de datos críticos

### **3. Desarrollo**
- ✅ **Entorno consistente**: Mismo setup en desarrollo y producción
- ✅ **Debugging**: Interfaces web para inspeccionar datos
- ✅ **Monitoreo**: Métricas en tiempo real

### **4. Mantenimiento**
- ✅ **Logs centralizados**: Todos los servicios en un lugar
- ✅ **Backup automático**: Volumes persistentes
- ✅ **Actualizaciones**: Rolling updates sin downtime

---

## 🚀 Comandos Útiles

### **Gestión de Servicios:**
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs de un servicio específico
docker logs cinemax_api

# Reiniciar un servicio
docker-compose restart api

# Escalar un servicio
docker-compose up -d --scale api=3
```

### **Monitoreo:**
```bash
# Ver estado de todos los servicios
docker-compose ps

# Ver uso de recursos
docker stats

# Acceder a un servicio específico
docker exec -it cinemax_api bash
```

### **Backup y Restore:**
```bash
# Backup de MongoDB
docker exec cinemax_mongodb mongodump --out /backup

# Backup de Redis
docker exec cinemax_redis redis-cli BGSAVE

# Backup de Prometheus
docker exec cinemax_prometheus promtool tsdb backup /prometheus
```

---

*🐳 Esta arquitectura distribuida permite que Cinemax API sea escalable, mantenible y fácil de monitorear, proporcionando una base sólida para el crecimiento futuro del proyecto.* 