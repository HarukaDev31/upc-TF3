# 🎬 Guía de Datos Masivos - Sistema de Cine

Esta guía te ayudará a generar datos masivos para probar el rendimiento de tu sistema de cine a gran escala.

## 📋 Contenido

- [Configuraciones Disponibles](#configuraciones-disponibles)
- [Generación de Datos](#generación-de-datos)
- [Limpieza de Datos](#limpieza-de-datos)
- [Monitoreo de Rendimiento](#monitoreo-de-rendimiento)
- [Troubleshooting](#troubleshooting)

## 🎯 Configuraciones Disponibles

### 📊 Niveles de Datos

| Nivel | Salas | Películas | Funciones | Clientes | Transacciones | Tiempo Estimado |
|-------|-------|-----------|-----------|----------|---------------|-----------------|
| **Pequeño** | 10 | 100 | 1,000 | 1,000 | 5,000 | 2-5 minutos |
| **Mediano** | 100 | 1,000 | 10,000 | 10,000 | 50,000 | 10-20 minutos |
| **Grande** | 1,000 | 50,000 | 1,000,000 | 100,000 | 500,000 | 30-60 minutos |
| **Masivo** | 5,000 | 200,000 | 5,000,000 | 500,000 | 2,000,000 | 2-4 horas |

### 🎬 Datos Generados

#### **Salas (1,000)**
- Tipos: estándar, vip, imax, 4dx, dolby, premium
- Capacidades: 50-200 asientos
- Equipamiento específico por tipo
- Asientos con filas y números

#### **Películas (50,000)**
- Títulos generados automáticamente
- 18 géneros diferentes
- Directores y actores realistas
- Fechas de estreno variadas
- Precios base: $8,000 - $18,000

#### **Funciones (1,000,000)**
- Distribuidas en los próximos 6 meses
- Estados: programada, en_venta, casi_agotada, agotada, cancelada
- Precios variables según sala y película
- Subtítulos y audio en múltiples idiomas

#### **Clientes (100,000)**
- Nombres y emails únicos
- Tipos: regular, frecuente, premium
- Puntos acumulados
- Historial de compras

#### **Transacciones (500,000)**
- Métodos de pago variados
- Estados: confirmada, pendiente, cancelada, reembolsada
- Facturas únicas
- Códigos QR simulados

## 🚀 Generación de Datos

### Opción 1: Script Automático (Recomendado)

```bash
# Dar permisos de ejecución
chmod +x scripts/run_massive_data.sh

# Ejecutar generación completa
./scripts/run_massive_data.sh
```

### Opción 2: Comandos Manuales

```bash
# 1. Verificar que los contenedores estén corriendo
docker-compose up -d

# 2. Esperar que MongoDB esté listo
docker exec cinemax_mongodb mongosh --eval "db.adminCommand('ping')"

# 3. Limpiar base de datos (opcional)
docker exec -i cinemax_mongodb mongosh cinemax < scripts/clean_database.js

# 4. Generar datos masivos
docker exec -i cinemax_mongodb mongosh cinemax < scripts/generate_massive_data.js
```

### Opción 3: Configuración Personalizada

Para cambiar la cantidad de datos, edita `scripts/generate_massive_data.js`:

```javascript
const CONFIG = {
    SALAS_TOTAL: 1000,        // Cambiar aquí
    PELICULAS_TOTAL: 50000,   // Cambiar aquí
    FUNCIONES_TOTAL: 1000000, // Cambiar aquí
    CLIENTES_TOTAL: 100000,   // Cambiar aquí
    TRANSACCIONES_TOTAL: 500000 // Cambiar aquí
};
```

## 🧹 Limpieza de Datos

### Limpiar Base de Datos Completa

```bash
# Ejecutar script de limpieza
docker exec -i cinemax_mongodb mongosh cinemax < scripts/clean_database.js
```

### Limpiar Volúmenes de Docker

```bash
# Detener contenedores
docker-compose down

# Eliminar volúmenes
docker volume rm upc_mongodb_data upc_redis_data

# Reiniciar
docker-compose up -d
```

## 📊 Monitoreo de Rendimiento

### URLs de Monitoreo

- **MongoDB Express**: http://localhost:8081
  - Usuario: `admin`
  - Contraseña: `admin123`

- **Redis Commander**: http://localhost:8082
  - Usuario: `admin`
  - Contraseña: `admin123`

- **Prometheus**: http://localhost:9090

- **Grafana**: http://localhost:3000
  - Usuario: `admin`
  - Contraseña: `admin123`

### Comandos de Verificación

```bash
# Verificar cantidad de documentos
docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.countDocuments()"
docker exec cinemax_mongodb mongosh cinemax --eval "db.funciones.countDocuments()"
docker exec cinemax_mongodb mongosh cinemax --eval "db.clientes.countDocuments()"

# Verificar índices
docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.getIndexes()"

# Verificar rendimiento de consultas
docker exec cinemax_mongodb mongosh cinemax --eval "db.peliculas.find({generos: 'accion'}).explain('executionStats')"
```

## 🎯 Pruebas de Rendimiento

### Consultas de Prueba

```javascript
// 1. Búsqueda de películas por género
db.peliculas.find({generos: "accion"}).limit(10)

// 2. Funciones próximas
db.funciones.find({
    fecha_hora_inicio: {
        $gte: new Date(),
        $lte: new Date(Date.now() + 7*24*60*60*1000)
    }
}).limit(20)

// 3. Clientes premium
db.clientes.find({tipo: "premium"}).limit(10)

// 4. Transacciones recientes
db.transacciones.find({
    fecha_creacion: {
        $gte: new Date(Date.now() - 30*24*60*60*1000)
    }
}).limit(20)

// 5. Estadísticas de ventas
db.transacciones.aggregate([
    {
        $group: {
            _id: "$estado",
            count: {$sum: 1},
            total: {$sum: "$monto_total"}
        }
    }
])
```

### Pruebas de API

```bash
# Health check
curl http://localhost:8000/health

# Listar películas con paginación
curl "http://localhost:8000/api/v1/peliculas?limite=10&offset=0"

# Buscar películas
curl -X POST http://localhost:8000/api/v1/buscar-peliculas \
  -H "Content-Type: application/json" \
  -d '{"texto": "accion", "limite": 20}'

# Comprar entrada
curl -X POST http://localhost:8000/api/v1/comprar-entrada \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "cliente_000001",
    "pelicula_id": "pel_000001",
    "funcion_id": "fun_000001",
    "asientos": ["A5", "A6"],
    "metodo_pago": "tarjeta"
  }'
```

## 🔧 Troubleshooting

### Problema: "Out of Memory"
**Solución:**
```bash
# Aumentar memoria de Docker
# En Docker Desktop: Settings > Resources > Memory > 4GB

# O reducir batch size en el script
const batchSize = 5000; // En lugar de 10000
```

### Problema: "Connection Timeout"
**Solución:**
```bash
# Verificar que MongoDB esté corriendo
docker logs cinemax_mongodb

# Reiniciar contenedores
docker-compose restart
```

### Problema: "Script se cuelga"
**Solución:**
```bash
# Verificar logs
docker logs cinemax_mongodb

# Limpiar y reiniciar
docker-compose down
docker volume rm upc_mongodb_data
docker-compose up -d
```

### Problema: "Datos no se generan"
**Solución:**
```bash
# Verificar permisos
chmod +x scripts/run_massive_data.sh

# Ejecutar manualmente
docker exec -i cinemax_mongodb mongosh cinemax < scripts/generate_massive_data.js
```

## 📈 Optimizaciones

### Índices Creados Automáticamente

- **Películas**: título, géneros, fecha_estreno, activa, director
- **Funciones**: pelicula_id, fecha_hora_inicio, estado, sala.id
- **Transacciones**: cliente_id, funcion_id, estado, fecha_creacion, numero_factura
- **Clientes**: email, tipo, activo

### Configuraciones de MongoDB

```javascript
// Optimizaciones aplicadas
db.adminCommand({
    setParameter: 1,
    maxTransactionLockRequestTimeoutMillis: 5000
});

// Índices compuestos para consultas complejas
db.funciones.createIndex({
    "pelicula_id": 1,
    "fecha_hora_inicio": 1,
    "estado": 1
});
```

## 🎬 Próximos Pasos

1. **Generar datos masivos**: Ejecuta `./scripts/run_massive_data.sh`
2. **Probar endpoints**: Usa la colección de Postman
3. **Monitorear rendimiento**: Revisa Grafana y Prometheus
4. **Optimizar consultas**: Analiza los logs de MongoDB
5. **Escalar horizontalmente**: Agrega más contenedores si es necesario

---

**¡Tu sistema de cine está listo para manejar datos masivos! 🎬✨** 