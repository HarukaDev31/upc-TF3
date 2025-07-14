# 📚 Documentación de Endpoints - Sistema de Cine

## 🎯 **Base URL:** `http://localhost:8000`

---

## 🎬 **1. Gestión de Usuarios** 
**Base Path:** `/api/v1/usuarios`

### 🔐 **Registro de Usuario**
```http
POST /api/v1/usuarios/registro
```

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "123456789",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "123456789",
  "fecha_registro": "2024-12-20T10:00:00Z",
  "activo": true
}
```

### 🔑 **Login de Usuario**
```http
POST /api/v1/usuarios/login
```

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "usuario": {
    "id": "507f1f77bcf86cd799439011",
    "email": "usuario@ejemplo.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "123456789",
    "fecha_registro": "2024-12-20T10:00:00Z",
    "activo": true
  },
  "mensaje": "Login exitoso"
}
```

### 👤 **Obtener Usuario por ID**
```http
GET /api/v1/usuarios/{usuario_id}
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "123456789",
  "fecha_registro": "2024-12-20T10:00:00Z",
  "activo": true
}
```

### 📋 **Listar Usuarios**
```http
GET /api/v1/usuarios/?skip=0&limit=100
```

**Query Parameters:**
- `skip` (int): Número de usuarios a saltar (paginación)
- `limit` (int): Número máximo de usuarios a retornar

**Response (200):**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "email": "usuario1@ejemplo.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "123456789",
    "fecha_registro": "2024-12-20T10:00:00Z",
    "activo": true
  },
  {
    "id": "507f1f77bcf86cd799439012",
    "email": "usuario2@ejemplo.com",
    "nombre": "María",
    "apellido": "García",
    "telefono": "987654321",
    "fecha_registro": "2024-12-20T11:00:00Z",
    "activo": true
  }
]
```

### ✏️ **Actualizar Usuario**
```http
PUT /api/v1/usuarios/{usuario_id}
```

**Request Body:**
```json
{
  "nombre": "Juan Carlos",
  "apellido": "Pérez López",
  "telefono": "987654321"
}
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "usuario@ejemplo.com",
  "nombre": "Juan Carlos",
  "apellido": "Pérez López",
  "telefono": "987654321",
  "fecha_registro": "2024-12-20T10:00:00Z",
  "activo": true
}
```

### 🚫 **Desactivar Usuario**
```http
DELETE /api/v1/usuarios/{usuario_id}
```

**Response (200):**
```json
{
  "mensaje": "Usuario desactivado exitosamente"
}
```

---

## 🎭 **2. Gestión de Selecciones de Asientos**
**Base Path:** `/api/v1/selecciones`

### 🪑 **Crear Selección de Asiento**
```http
POST /api/v1/selecciones/
```

**Request Body:**
```json
{
  "funcion_id": "fun_001",
  "usuario_id": "507f1f77bcf86cd799439011",
  "asiento_id": "A1",
  "estado": "temporal"
}
```

**Response (201):**
```json
{
  "seleccion": {
    "id": "507f1f77bcf86cd799439020",
    "funcion_id": "fun_001",
    "usuario_id": "507f1f77bcf86cd799439011",
    "asiento_id": "A1",
    "estado": "temporal",
    "fecha_seleccion": "2024-12-20T10:00:00Z",
    "fecha_expiracion": "2024-12-20T10:05:00Z",
    "fecha_confirmacion": null,
    "fecha_cancelacion": null
  },
  "mensaje": "Asiento seleccionado exitosamente"
}
```

### 🔍 **Obtener Selección por ID**
```http
GET /api/v1/selecciones/{seleccion_id}
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439020",
  "funcion_id": "fun_001",
  "usuario_id": "507f1f77bcf86cd799439011",
  "asiento_id": "A1",
  "estado": "temporal",
  "fecha_seleccion": "2024-12-20T10:00:00Z",
  "fecha_expiracion": "2024-12-20T10:05:00Z",
  "fecha_confirmacion": null,
  "fecha_cancelacion": null
}
```

### 🎬 **Obtener Selecciones por Función**
```http
GET /api/v1/selecciones/funcion/{funcion_id}
```

**Response (200):**
```json
[
  {
    "id": "507f1f77bcf86cd799439020",
    "funcion_id": "fun_001",
    "usuario_id": "507f1f77bcf86cd799439011",
    "asiento_id": "A1",
    "estado": "temporal",
    "fecha_seleccion": "2024-12-20T10:00:00Z",
    "fecha_expiracion": "2024-12-20T10:05:00Z",
    "fecha_confirmacion": null,
    "fecha_cancelacion": null
  },
  {
    "id": "507f1f77bcf86cd799439021",
    "funcion_id": "fun_001",
    "usuario_id": "507f1f77bcf86cd799439012",
    "asiento_id": "A2",
    "estado": "confirmada",
    "fecha_seleccion": "2024-12-20T09:00:00Z",
    "fecha_expiracion": null,
    "fecha_confirmacion": "2024-12-20T09:05:00Z",
    "fecha_cancelacion": null
  }
]
```

### 👤 **Obtener Selecciones por Usuario**
```http
GET /api/v1/selecciones/usuario/{usuario_id}
```

**Response (200):**
```json
[
  {
    "id": "507f1f77bcf86cd799439020",
    "funcion_id": "fun_001",
    "usuario_id": "507f1f77bcf86cd799439011",
    "asiento_id": "A1",
    "estado": "temporal",
    "fecha_seleccion": "2024-12-20T10:00:00Z",
    "fecha_expiracion": "2024-12-20T10:05:00Z",
    "fecha_confirmacion": null,
    "fecha_cancelacion": null
  }
]
```

### ✅ **Confirmar Selección**
```http
POST /api/v1/selecciones/{seleccion_id}/confirmar
```

**Response (200):**
```json
{
  "mensaje": "Selección confirmada exitosamente"
}
```

### ❌ **Cancelar Selección**
```http
POST /api/v1/selecciones/{seleccion_id}/cancelar
```

**Response (200):**
```json
{
  "mensaje": "Selección cancelada exitosamente"
}
```

### 📊 **Obtener Historial de Función**
```http
GET /api/v1/selecciones/funcion/{funcion_id}/historial
```

**Response (200):**
```json
{
  "funcion_id": "fun_001",
  "selecciones": [
    {
      "id": "507f1f77bcf86cd799439020",
      "funcion_id": "fun_001",
      "usuario_id": "507f1f77bcf86cd799439011",
      "asiento_id": "A1",
      "estado": "temporal",
      "fecha_seleccion": "2024-12-20T10:00:00Z",
      "fecha_expiracion": "2024-12-20T10:05:00Z",
      "fecha_confirmacion": null,
      "fecha_cancelacion": null
    },
    {
      "id": "507f1f77bcf86cd799439021",
      "funcion_id": "fun_001",
      "usuario_id": "507f1f77bcf86cd799439012",
      "asiento_id": "A2",
      "estado": "confirmada",
      "fecha_seleccion": "2024-12-20T09:00:00Z",
      "fecha_expiracion": null,
      "fecha_confirmacion": "2024-12-20T09:05:00Z",
      "fecha_cancelacion": null
    }
  ],
  "total_selecciones": 2,
  "selecciones_temporales": 1,
  "selecciones_confirmadas": 1,
  "selecciones_canceladas": 0
}
```

### 🧹 **Limpiar Selecciones Expiradas**
```http
POST /api/v1/selecciones/limpiar-expiradas
```

**Response (200):**
```json
{
  "mensaje": "Se limpiaron 5 selecciones expiradas",
  "selecciones_limpiadas": 5
}
```

---

## 🌐 **3. WebSocket Endpoints**

### 🔌 **WebSocket Genérico**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{client_id}');
```

### 🎭 **WebSocket para Selección de Asientos**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/funciones/{funcion_id}/asientos');
```

**Mensajes WebSocket:**

#### **Seleccionar Asiento:**
```json
{
  "action": "select",
  "asientos": ["A1", "A2"]
}
```

#### **Deseleccionar Asiento:**
```json
{
  "action": "deselect",
  "asientos": ["A1"]
}
```

---

## 📋 **4. Estados de Selección**

| Estado | Descripción | Duración |
|--------|-------------|----------|
| `temporal` | Selección temporal | 5 minutos |
| `confirmada` | Selección confirmada | Permanente |
| `cancelada` | Selección cancelada | Permanente |
| `expirada` | Selección expirada | Permanente |

---

## 🔧 **5. Códigos de Error Comunes**

| Código | Descripción |
|--------|-------------|
| `400` | Datos inválidos o asiento ya seleccionado |
| `401` | Credenciales inválidas |
| `404` | Recurso no encontrado |
| `503` | Servicio de base de datos no disponible |
| `500` | Error interno del servidor |

---

## 🚀 **6. Ejemplos de Uso**

### **Flujo Completo de Registro y Selección:**

#### **1. Registrar usuario:**
```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/registro" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "123456789",
    "password": "password123"
  }'
```

#### **2. Hacer login:**
```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123"
  }'
```

#### **3. Ver historial de función:**
```bash
curl "http://localhost:8000/api/v1/selecciones/funcion/fun_001/historial"
```

#### **4. Conectar WebSocket:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/funciones/fun_001/asientos');
ws.send(JSON.stringify({
  "action": "select",
  "asientos": ["A1", "A2"]
}));
```

---

## 📖 **7. Documentación Interactiva**

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva en:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

¡Todos los endpoints están documentados automáticamente con ejemplos y esquemas! 🎉

---

## 🔐 **8. Características de Seguridad**

- **Encriptación de passwords** con bcrypt
- **Validación de emails** con email-validator
- **Validación de asientos** (no permite duplicados)
- **Estados de selección** con expiración automática
- **Manejo de errores** robusto

---

## 📊 **9. Monitoreo y Métricas**

- **Health Check:** `GET /health`
- **Métricas:** `GET /metrics` (si está habilitado)
- **Logs:** Disponibles en `logs/` directory

---

## 🛠️ **10. Configuración del Entorno**

### **Variables de Entorno:**
```bash
MONGODB_URL=mongodb://admin:password123@mongodb:27017/cinemax?authSource=admin
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123
REDIS_DB=0
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Cine
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
ENABLE_METRICS=true
METRICS_PORT=8000
REDIS_POOL_MAX_CONNECTIONS=50
MONGODB_MAX_CONNECTIONS=100
WEBSOCKET_PORT=8001
WEBSOCKET_HOST=0.0.0.0
```

---

## 📝 **11. Notas de Desarrollo**

- **Base de datos:** MongoDB con Motor (async)
- **Cache:** Redis para WebSocket y sesiones
- **Framework:** FastAPI con Pydantic
- **WebSocket:** Integrado con FastAPI
- **Autenticación:** bcrypt para passwords
- **Validación:** Pydantic con email-validator

---

## 🎯 **12. Próximas Mejoras**

- [ ] Implementar JWT para autenticación
- [ ] Agregar roles de usuario (admin, cliente)
- [ ] Implementar notificaciones push
- [ ] Agregar métricas avanzadas
- [ ] Implementar rate limiting
- [ ] Agregar tests automatizados
- [ ] Implementar backup automático
- [ ] Agregar documentación de deployment

---

*Documentación generada automáticamente - Sistema de Cine v1.0.0* 🎬 