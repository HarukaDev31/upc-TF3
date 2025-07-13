# 🎬 Sistema de Cine - API REST

Sistema avanzado de venta de entradas de cine con arquitectura escalable usando FastAPI, MongoDB y Redis.

## 🏗️ Arquitectura

### Estructura del Proyecto

```
upc-TF3/
├── controllers/                 # Controladores separados por responsabilidad
│   ├── __init__.py
│   ├── peliculas_controller.py  # Gestión de películas
│   ├── funciones_controller.py  # Gestión de funciones y asientos
│   ├── transacciones_controller.py # Compra de entradas
│   └── metricas_controller.py  # Reportes y métricas
├── use_cases/                  # Casos de uso de negocio
│   ├── __init__.py
│   └── comprar_entrada_use_case.py
├── infrastructure/             # Capa de infraestructura
│   ├── database/
│   │   └── mongodb_service.py
│   └── cache/
│       └── redis_service.py
├── domain/                     # Entidades de dominio
│   ├── entities/
│   └── repositories/
├── config/                     # Configuración
│   └── settings.py
├── main.py                     # Punto de entrada
└── requirements.txt
```

## 🚀 Características Principales

### ✅ Conexión Optimizada a MongoDB
- **Motor Async**: Uso de `motor` para operaciones asíncronas
- **Índices Optimizados**: Índices de texto y compuestos para consultas rápidas
- **Pool de Conexiones**: Configuración optimizada para alta concurrencia
- **Validación de Conexión**: Health checks automáticos

### 🎯 Controladores Separados por Responsabilidad

#### 1. **PeliculasController** (`/api/v1/peliculas`)
- Listar películas con paginación
- Obtener película específica
- Búsqueda avanzada con filtros
- Funciones de una película

#### 2. **FuncionesController** (`/api/v1/funciones`)
- Mapa de asientos en tiempo real
- Información detallada de funciones
- Reserva temporal de asientos

#### 3. **TransaccionesController** (`/api/v1/transacciones`)
- Compra de entradas optimizada
- Gestión de transacciones
- Cancelación de compras

#### 4. **MetricasController** (`/api/v1/metricas`)
- Ranking de películas más vendidas
- Ocupación de salas en tiempo real
- Métricas de ventas por período
- Dashboard con resumen general

### 🔄 Casos de Uso
- **ComprarEntradaUseCase**: Lógica de negocio para compra de entradas
- Validaciones de disponibilidad
- Procesamiento de pagos
- Actualización de métricas

## 🛠️ Instalación y Configuración

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
Crear archivo `.env`:
```env
# MongoDB
MONGODB_URL=mongodb://admin:password123@localhost:27017
MONGODB_DATABASE=cinemax

# Redis
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=

# Aplicación
ENVIRONMENT=development
DEBUG=true
```

### 3. Ejecutar con Docker
```bash
docker-compose up -d
```

### 4. Ejecutar Localmente
```bash
python main.py
```

## 📚 API Endpoints

### 🎬 Películas
```
GET    /api/v1/peliculas/                    # Listar películas
GET    /api/v1/peliculas/{id}                # Obtener película
POST   /api/v1/peliculas/buscar              # Búsqueda avanzada
GET    /api/v1/peliculas/{id}/funciones      # Funciones de película
```

### 🎭 Funciones
```
GET    /api/v1/funciones/{id}                # Información de función
GET    /api/v1/funciones/{id}/asientos       # Mapa de asientos
POST   /api/v1/funciones/{id}/reservar-asientos # Reserva temporal
```

### 💰 Transacciones
```
POST   /api/v1/transacciones/comprar-entrada # Comprar entrada
GET    /api/v1/transacciones/{id}            # Obtener transacción
GET    /api/v1/transacciones/cliente/{id}    # Transacciones de cliente
POST   /api/v1/transacciones/{id}/cancelar   # Cancelar transacción
```

### 📊 Métricas
```
GET    /api/v1/metricas/ranking-peliculas    # Ranking de ventas
GET    /api/v1/metricas/ocupacion/{id}       # Ocupación de sala
GET    /api/v1/metricas/ventas/periodo       # Métricas por período
GET    /api/v1/metricas/dashboard/resumen     # Resumen general
```

## 🔧 Mejoras Implementadas

### 1. **Separación de Responsabilidades**
- ✅ Controladores separados por dominio
- ✅ Casos de uso para lógica de negocio
- ✅ Servicios de infraestructura optimizados

### 2. **Conexión MongoDB Mejorada**
- ✅ Configuración async con motor
- ✅ Índices optimizados para consultas
- ✅ Métodos adicionales para controladores
- ✅ Manejo de errores robusto

### 3. **Redis Optimizado**
- ✅ Métodos para gestión de asientos
- ✅ Reservas temporales
- ✅ Métricas en tiempo real
- ✅ Limpieza automática

### 4. **Arquitectura Escalable**
- ✅ Patrón Repository
- ✅ Inyección de dependencias
- ✅ Manejo de errores centralizado
- ✅ Logging estructurado

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Tests con coverage
pytest --cov=.

# Tests de integración
pytest tests/integration/
```

## 📈 Monitoreo

### Health Check
```bash
curl http://localhost:8000/health
```

### Métricas Prometheus
```bash
curl http://localhost:8000/metrics
```

## 🚀 Despliegue

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 📝 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman Collection**: `Cinemax_API.postman_collection.json`

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**🎬 ¡Disfruta del cine con tecnología de punta!** 