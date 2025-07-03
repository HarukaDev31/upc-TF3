# 🎬 Sistema de Cine - FastAPI + Redis + MongoDB

Sistema avanzado de venta de entradas de cine implementando Clean Architecture con algoritmos optimizados para alto rendimiento.

## 🚀 Características Principales

- **Algoritmo de Compra Optimizado**: Complejidad O(log n) usando Redis Bitmaps
- **Cache Inteligente**: Redis para operaciones de alta frecuencia
- **Persistencia Robusta**: MongoDB para datos transaccionales
- **Arquitectura Limpia**: Separación clara de responsabilidades
- **API RESTful**: FastAPI con documentación automática
- **Concurrencia Segura**: Locks distribuidos con Redis
- **Métricas en Tiempo Real**: Dashboards y analytics

## 🏗️ Arquitectura del Sistema

```
├── domain/                 # Entidades de negocio y reglas
│   ├── entities/          # Modelos de dominio
│   └── repositories/      # Interfaces (puertos)
├── application/           # Casos de uso
│   └── use_cases/        # Lógica de aplicación
├── infrastructure/       # Implementaciones técnicas
│   ├── cache/           # Servicios de Redis
│   ├── database/        # Servicios de MongoDB
│   └── external/        # Servicios externos
├── config/               # Configuración
└── main.py              # Aplicación FastAPI
```

## 📋 Requisitos Previos

- Python 3.9+
- Redis Server
- MongoDB
- Git

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd UPC
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Crear archivo .env basado en .env.example
cp .env.example .env

# Editar .env con tus configuraciones
```

### 5. Iniciar servicios de base de datos

#### Redis

**Para Windows (Recomendado: usar WSL)**
```bash
# 1. Instalar WSL2 si no lo tienes
wsl --install

# 2. Entrar a WSL
wsl

# 3. Instalar Redis en WSL (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server

# 4. Configurar Redis para iniciar automáticamente
sudo systemctl enable redis-server

# 5. Iniciar Redis
sudo systemctl start redis-server

# 6. Verificar que Redis está funcionando
redis-cli ping
# Debería responder: PONG

# 7. Configurar Redis para aceptar conexiones externas (opcional)
sudo nano /etc/redis/redis.conf
# Comentar o cambiar: bind 127.0.0.1 ::1
# A: bind 0.0.0.0

# 8. Reiniciar Redis
sudo systemctl restart redis-server
```

**Para Windows (Nativo - No recomendado)**
```bash
# Solo si no puedes usar WSL
choco install redis-64
redis-server
```

**Para Ubuntu/Debian (Nativo)**
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Para Mac**
```bash
brew install redis
brew services start redis
```

**Verificar conexión desde Windows a WSL**
```bash
# Obtener IP de WSL
wsl hostname -I

# Desde PowerShell/CMD en Windows, probar conexión
# Reemplaza [WSL_IP] con la IP obtenida
telnet [WSL_IP] 6379
```

#### MongoDB
```bash
# Windows
# Descargar desde https://www.mongodb.com/try/download/community

# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongod

# Mac
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

## 🚀 Ejecución

### Desarrollo
```bash
python main.py
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servidor estará disponible en: http://localhost:8000

## 📚 Documentación de API

Una vez ejecutando el servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔥 Endpoints Principales

### Compra de Entradas
```http
POST /api/v1/comprar-entrada
Content-Type: application/json

{
  "cliente_id": "cliente_123",
  "pelicula_id": "pel_001",
  "funcion_id": "fun_001",
  "asientos": ["A5", "A6"],
  "metodo_pago": "tarjeta_credito"
}
```

### Listar Películas
```http
GET /api/v1/peliculas?limite=20&offset=0
```

### Obtener Funciones
```http
GET /api/v1/peliculas/pel_001/funciones
```

### Mapa de Asientos
```http
GET /api/v1/funciones/fun_001/asientos
```

### Búsqueda de Películas
```http
POST /api/v1/buscar-peliculas
Content-Type: application/json

{
  "texto": "avengers",
  "genero": "accion",
  "limite": 10
}
```

### Métricas en Tiempo Real
```http
GET /api/v1/metricas/ranking-peliculas
GET /api/v1/metricas/ocupacion/fun_001
```

## ⚡ Algoritmo de Compra Optimizado

El sistema implementa un algoritmo de compra con las siguientes optimizaciones:

### 1. Validación con Cache (O(1))
- Redis Hash para datos de cliente frecuentes
- TTL automático para cache invalidation

### 2. Verificación de Asientos (O(k))
- Redis Bitmaps para estado de asientos
- Pipeline para verificaciones múltiples

### 3. Reserva Temporal (O(k))
- Locks distribuidos con Redlock
- TTL automático para liberación de reservas

### 4. Persistencia Transaccional (O(1))
- MongoDB con índices optimizados
- Write concern para consistencia

### 5. Métricas en Tiempo Real
- Redis Sorted Sets para rankings
- HyperLogLog para conteos únicos
- Streams para eventos en tiempo real

## 🗄️ Estructura de Datos

### Redis
```
# Cache de clientes
cliente:{id} -> Hash {nombre, email, tipo}

# Estado de asientos (bitmap)
sala:asientos:{funcion_id} -> Bitmap

# Reservas temporales
reserva:{id} -> Hash {cliente_id, asientos, timestamp}

# Rankings
ranking:peliculas:ventas -> Sorted Set

# Métricas
metricas:pelicula:{id} -> Hash {ventas_total, ...}

# Eventos
stream:ventas -> Stream
```

### MongoDB
```javascript
// Colección: clientes
{
  _id: "cliente_123",
  nombre: "Juan Pérez",
  email: "juan@email.com",
  tipo: "premium"
}

// Colección: peliculas  
{
  _id: "pel_001",
  titulo: "Avengers: Endgame",
  director: "Russo Brothers",
  generos: ["accion", "aventura"]
}

// Colección: transacciones
{
  _id: "trx_001",
  cliente_id: "cliente_123",
  funcion_id: "fun_001",
  asientos: [...],
  total: 30000,
  estado: "confirmado"
}
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html
```

## 🚨 Monitoreo y Health Checks

```http
GET /health
```

Respuesta:
```json
{
  "estado": "saludable",
  "servicios": {
    "redis": "conectado",
    "mongodb": "conectado"
  }
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Base de datos
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=cinemax

# Redis (configuración automática según el setup)
REDIS_HOST=localhost  # o IP de WSL si se detecta automáticamente
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Aplicación
SECRET_KEY=tu-clave-secreta
DEBUG=true
```

### Configuración específica para WSL
```bash
# Si usas Redis en WSL, el setup automático configurará:
REDIS_HOST=[IP_DE_WSL]  # Ej: 172.20.0.2

# Si tienes problemas de conectividad, prueba:
REDIS_HOST=localhost    # WSL2 debería hacer port forwarding automático

# Para obtener la IP de WSL manualmente:
wsl hostname -I
```

### Performance Tuning
```python
# Redis Pool
REDIS_POOL_MAX_CONNECTIONS=50

# MongoDB
MONGODB_MAX_CONNECTIONS=100

# FastAPI Workers (producción)
uvicorn main:app --workers 4
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Equipo

- **Desarrollador Principal**: Tu Nombre
- **Arquitectura**: Clean Architecture + DDD
- **Stack**: FastAPI + Redis + MongoDB + Docker

## 🔮 Roadmap

- [ ] Implementación completa del algoritmo de compra
- [ ] Sistema de autenticación JWT
- [ ] WebSockets para notificaciones en tiempo real
- [ ] Dashboard de administración
- [ ] Integración con gateways de pago reales
- [ ] Containerización con Docker
- [ ] CI/CD con GitHub Actions
- [ ] Monitoring con Prometheus + Grafana

## 🛠️ Troubleshooting WSL + Redis

### Problema: No se puede conectar a Redis en WSL
**Solución 1: Verificar que Redis esté corriendo**
```bash
# Entrar a WSL
wsl

# Verificar estado de Redis
sudo systemctl status redis-server

# Si no está activo, iniciarlo
sudo systemctl start redis-server
```

**Solución 2: Verificar configuración de bind**
```bash
# En WSL, editar configuración de Redis
sudo nano /etc/redis/redis.conf

# Buscar la línea que dice:
# bind 127.0.0.1 ::1

# Cambiarla por (para permitir conexiones externas):
bind 0.0.0.0

# Reiniciar Redis
sudo systemctl restart redis-server
```

**Solución 3: Usar localhost en lugar de IP**
```bash
# En tu archivo .env, cambiar:
REDIS_HOST=localhost
# En lugar de usar la IP de WSL
```

**Solución 4: Verificar firewall de Windows**
```powershell
# En PowerShell como administrador
New-NetFirewallRule -DisplayName "WSL Redis" -Direction Inbound -Protocol TCP -LocalPort 6379 -Action Allow
```

### Problema: WSL no se detecta en el setup
**Solución:**
```bash
# Verificar que WSL esté instalado
wsl --list --verbose

# Si no hay distribuciones, instalar:
wsl --install

# Actualizar WSL
wsl --update
```

### Problema: IP de WSL cambia constantemente
**Solución: Usar configuración estática**
```bash
# En archivo .env, usar siempre:
REDIS_HOST=localhost

# WSL2 debería hacer port forwarding automáticamente
```

### Comandos útiles para diagnóstico
```bash
# Obtener IP de WSL
wsl hostname -I

# Probar conexión a Redis desde WSL
wsl redis-cli ping

# Probar conexión a Redis desde Windows
telnet [WSL_IP] 6379

# Ver logs de Redis
wsl sudo journalctl -u redis-server -f

# Verificar puertos abiertos en WSL
wsl ss -tlnp | grep 6379
```

---

¡Gracias por usar nuestro Sistema de Cine! 🍿🎭 