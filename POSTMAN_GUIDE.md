# 🎬 Guía de Pruebas con Postman - Sistema de Cine

Esta guía te ayudará a importar y usar la colección de Postman para probar todos los endpoints de la API del Sistema de Cine.

## 📋 Contenido

- [Importar Colección](#importar-colección)
- [Configurar Entorno](#configurar-entorno)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Troubleshooting](#troubleshooting)

## 📥 Importar Colección

### 1. Importar la Colección
1. Abre Postman
2. Haz clic en **Import**
3. Selecciona el archivo `Cinemax_API.postman_collection.json`
4. Haz clic en **Import**

### 2. Importar el Entorno
1. En Postman, ve a **Environments**
2. Haz clic en **Import**
3. Selecciona el archivo `Cinemax_API.postman_environment.json`
4. Haz clic en **Import**

### 3. Seleccionar el Entorno
1. En la esquina superior derecha, selecciona **"Cinemax API - Environment"**
2. Verifica que las variables estén configuradas correctamente

## ⚙️ Configurar Entorno

### Variables del Entorno
- `base_url`: `http://localhost:8000` (URL de la API)
- `pelicula_id`: `pel_001` (ID de película de ejemplo)
- `funcion_id`: `fun_001` (ID de función de ejemplo)
- `cliente_id`: `cliente_001` (ID de cliente de ejemplo)
- `auth_token`: (Para futuras implementaciones de autenticación)

### Verificar Configuración
1. Ve a **Environments** → **Cinemax API - Environment**
2. Verifica que `base_url` sea `http://localhost:8000`
3. Guarda los cambios

## 🎯 Endpoints Disponibles

### 🏠 Endpoints Básicos
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Bienvenida de la API |
| `/health` | GET | Estado de salud de servicios |

### 🎬 Gestión de Películas
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/peliculas` | GET | Listar películas con paginación |
| `/api/v1/peliculas/{id}/funciones` | GET | Funciones de una película |
| `/api/v1/buscar-peliculas` | POST | Buscar películas por criterios |

### 🎭 Gestión de Funciones
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/funciones/{id}/asientos` | GET | Asientos de una función |

### 🎫 Compra de Entradas
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/comprar-entrada` | POST | Comprar entradas |

### 📊 Métricas y Analytics
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/metricas/ranking-peliculas` | GET | Ranking de películas |
| `/api/v1/metricas/ocupacion/{id}` | GET | Ocupación de sala |

## 🚀 Ejemplos de Uso

### 1. Verificar Estado de la API
```bash
# GET http://localhost:8000/
# GET http://localhost:8000/health
```

### 2. Listar Películas
```bash
# GET http://localhost:8000/api/v1/peliculas?limite=10&offset=0
```

### 3. Obtener Funciones de una Película
```bash
# GET http://localhost:8000/api/v1/peliculas/pel_001/funciones
```

### 4. Comprar Entradas
```bash
# POST http://localhost:8000/api/v1/comprar-entrada
{
  "cliente_id": "cliente_001",
  "pelicula_id": "pel_001",
  "funcion_id": "fun_001",
  "asientos": ["A5", "A6"],
  "metodo_pago": "tarjeta"
}
```

### 5. Buscar Películas
```bash
# POST http://localhost:8000/api/v1/buscar-peliculas
{
  "texto": "Avengers",
  "genero": "accion",
  "fecha": "2024-12-20",
  "limite": 10
}
```

## 🔧 Troubleshooting

### Problema: "Connection refused"
**Solución:**
1. Verifica que Docker esté corriendo
2. Ejecuta: `docker-compose up -d`
3. Verifica que la API esté en `http://localhost:8000`

### Problema: "404 Not Found"
**Solución:**
1. Verifica que la URL base sea correcta
2. Asegúrate de que el entorno esté seleccionado
3. Verifica que la API esté funcionando

### Problema: "500 Internal Server Error"
**Solución:**
1. Revisa los logs de Docker: `docker logs cinemax_api`
2. Verifica que MongoDB y Redis estén conectados
3. Reinicia los contenedores: `docker-compose restart`

### Problema: Variables no funcionan
**Solución:**
1. Verifica que el entorno esté seleccionado
2. Revisa las variables en **Environments**
3. Asegúrate de que las variables estén habilitadas

## 📊 Monitoreo

### URLs de Monitoreo
- **API Docs**: http://localhost:8000/docs
- **MongoDB Express**: http://localhost:8081
- **Redis Commander**: http://localhost:8082
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### Credenciales de Acceso
- **MongoDB Express**: admin / admin123
- **Redis Commander**: admin / admin123
- **Grafana**: admin / admin123

## 🎯 Pruebas Recomendadas

### 1. Flujo Completo de Compra
1. Listar películas
2. Obtener funciones de una película
3. Ver asientos disponibles
4. Comprar entradas
5. Verificar métricas

### 2. Pruebas de Rendimiento
1. Health check
2. Múltiples peticiones simultáneas
3. Verificar tiempos de respuesta

### 3. Pruebas de Error
1. IDs inexistentes
2. Datos inválidos
3. Servicios no disponibles

## 📝 Notas Importantes

- La API usa **FastAPI** con **Redis** y **MongoDB**
- Todos los endpoints devuelven **JSON**
- Los errores siguen el estándar **HTTP**
- La documentación automática está en `/docs`
- Los tests automáticos validan respuestas básicas

## 🔄 Actualizaciones

Para actualizar la colección:
1. Exporta la colección actualizada
2. Reemplaza el archivo JSON
3. Importa la nueva versión
4. Verifica que las variables estén correctas

---

**¡Disfruta probando tu API del Sistema de Cine! 🎬✨** 