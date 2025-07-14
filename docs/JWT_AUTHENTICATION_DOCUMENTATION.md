# Documentación de Autenticación JWT - Sistema de Cine

## Descripción General

El sistema de cine implementa autenticación JWT (JSON Web Tokens) para proporcionar acceso seguro a los usuarios registrados. Los tokens JWT contienen información esencial del usuario y tienen una duración de 30 minutos.

## Configuración JWT

- **Algoritmo**: HS256
- **Duración del token**: 30 minutos
- **Tipo de token**: Bearer
- **Clave secreta**: Configurable mediante variable de entorno `JWT_SECRET_KEY`

## Endpoints de Autenticación

### 1. Registro de Usuario

**Endpoint**: `POST /api/v1/usuarios/registro`

**Descripción**: Registra un nuevo usuario y devuelve un token JWT de acceso.

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+573001234567",
  "password": "contraseña123"
}
```

**Respuesta Exitosa** (200):
```json
{
  "usuario": {
    "id": "507f1f77bcf86cd799439011",
    "email": "usuario@ejemplo.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+573001234567",
    "fecha_registro": "2024-01-15T10:30:00Z",
    "activo": true
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 30
  },
  "mensaje": "Usuario registrado exitosamente"
}
```

**Errores**:
- `400 Bad Request`: Email ya registrado
- `503 Service Unavailable`: Servicio de base de datos no disponible
- `500 Internal Server Error`: Error interno del servidor

### 2. Login de Usuario

**Endpoint**: `POST /api/v1/usuarios/login`

**Descripción**: Autentica un usuario existente y devuelve un token JWT de acceso.

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Respuesta Exitosa** (200):
```json
{
  "usuario": {
    "id": "507f1f77bcf86cd799439011",
    "email": "usuario@ejemplo.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+573001234567",
    "fecha_registro": "2024-01-15T10:30:00Z",
    "activo": true
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 30
  },
  "mensaje": "Login exitoso"
}
```

**Errores**:
- `401 Unauthorized`: Credenciales inválidas
- `503 Service Unavailable`: Servicio de base de datos no disponible
- `500 Internal Server Error`: Error interno del servidor

### 3. Obtener Usuario Actual

**Endpoint**: `GET /api/v1/usuarios/me`

**Descripción**: Obtiene la información del usuario actual desde el token JWT.

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Respuesta Exitosa** (200):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+573001234567",
  "fecha_registro": "2024-01-15T10:30:00Z",
  "activo": true
}
```

**Errores**:
- `401 Unauthorized`: Token inválido, expirado o no proporcionado
- `404 Not Found`: Usuario no encontrado
- `503 Service Unavailable`: Servicio de base de datos no disponible
- `500 Internal Server Error`: Error interno del servidor

## Estructura del Token JWT

El token JWT contiene la siguiente información:

```json
{
  "sub": "507f1f77bcf86cd799439011",
  "email": "usuario@ejemplo.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "exp": 1705312800
}
```

### Campos del Token:
- **sub**: ID único del usuario
- **email**: Email del usuario
- **nombre**: Nombre del usuario
- **apellido**: Apellido del usuario
- **exp**: Timestamp de expiración

## Uso del Token

### En Headers HTTP:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### En JavaScript/Fetch:
```javascript
const response = await fetch('/api/v1/usuarios/me', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### En cURL:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:8000/api/v1/usuarios/me
```

## Seguridad

### Características de Seguridad:
1. **Contraseñas hasheadas**: Las contraseñas se almacenan usando bcrypt
2. **Tokens con expiración**: Los tokens expiran automáticamente
3. **Información mínima**: Los tokens solo contienen información esencial
4. **Validación estricta**: Verificación completa de tokens en cada request

### Mejores Prácticas:
1. **Almacenamiento seguro**: Guardar tokens en localStorage o sessionStorage
2. **Renovación automática**: Implementar renovación de tokens antes de expirar
3. **Logout seguro**: Eliminar tokens al cerrar sesión
4. **HTTPS**: Usar siempre HTTPS en producción

## Ejemplos de Uso

### Registro de Usuario:
```javascript
const registrarUsuario = async (datosUsuario) => {
  const response = await fetch('/api/v1/usuarios/registro', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(datosUsuario)
  });
  
  const resultado = await response.json();
  
  if (response.ok) {
    // Guardar token
    localStorage.setItem('token', resultado.token.access_token);
    return resultado;
  } else {
    throw new Error(resultado.detail);
  }
};
```

### Login de Usuario:
```javascript
const loginUsuario = async (email, password) => {
  const response = await fetch('/api/v1/usuarios/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const resultado = await response.json();
  
  if (response.ok) {
    // Guardar token
    localStorage.setItem('token', resultado.token.access_token);
    return resultado;
  } else {
    throw new Error(resultado.detail);
  }
};
```

### Obtener Usuario Actual:
```javascript
const obtenerUsuarioActual = async () => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('No hay token de autenticación');
  }
  
  const response = await fetch('/api/v1/usuarios/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    return await response.json();
  } else {
    // Token expirado o inválido
    localStorage.removeItem('token');
    throw new Error('Token inválido');
  }
};
```

### Logout:
```javascript
const logout = () => {
  localStorage.removeItem('token');
  // Redirigir a login
  window.location.href = '/login';
};
```

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | Operación exitosa |
| 400 | Datos de entrada inválidos |
| 401 | No autorizado (token inválido o credenciales incorrectas) |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |
| 503 | Servicio no disponible |

## Configuración del Entorno

### Variables de Entorno:
```bash
# Clave secreta para JWT (cambiar en producción)
JWT_SECRET_KEY=tu_clave_secreta_super_segura_cambiala_en_produccion

# Configuración de la base de datos
MONGODB_URL=mongodb://localhost:27017/cinemax
```

### Docker Compose:
```yaml
environment:
  - JWT_SECRET_KEY=tu_clave_secreta_super_segura_cambiala_en_produccion
```

## Notas Importantes

1. **Cambiar la clave secreta**: En producción, cambiar la clave secreta por defecto
2. **HTTPS**: Usar siempre HTTPS en producción
3. **Renovación de tokens**: Implementar renovación automática de tokens
4. **Logout**: Implementar logout seguro eliminando tokens
5. **Validación**: Validar tokens en cada request que requiera autenticación

## Integración con Otros Endpoints

Para usar autenticación en otros endpoints, agregar la dependencia:

```python
from controllers.usuarios_controller import get_current_user

@router.get("/endpoint-protegido")
async def endpoint_protegido(current_user: dict = Depends(get_current_user)):
    # El usuario está autenticado
    return {"mensaje": f"Hola {current_user['nombre']}"}
``` 