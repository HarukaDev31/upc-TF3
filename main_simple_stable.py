from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import uvicorn
import logging

from config.settings import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Servicios globales - Inicializar como None por ahora
redis_service = None
mongodb_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando Sistema de Cine...")
    
    try:
        # Intentar conectar a Redis
        try:
            from infrastructure.cache.redis_service import RedisService
            global redis_service
            redis_service = RedisService()
            await redis_service.connect()
            logger.info("✅ Conectado a Redis")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo conectar a Redis: {e}")
            logger.info("📝 Continuando sin Redis...")
        
        # MongoDB deshabilitado temporalmente para desarrollo
        logger.info("📝 MongoDB deshabilitado temporalmente para desarrollo")
        
        logger.info("🎬 Sistema de Cine listo!")
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar: {e}")
        logger.info("📝 Continuando con funcionalidad limitada...")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando conexiones...")
    if redis_service:
        try:
            await redis_service.disconnect()
        except Exception as e:
            logger.error(f"Error al desconectar Redis: {e}")
    logger.info("👋 ¡Hasta luego!")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.project_name,
    description="Sistema avanzado de venta de entradas de cine con Redis y MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints principales
@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    try:
        return JSONResponse(
            status_code=200,
            content={
                "mensaje": "🎬 Sistema de Cine - API",
                "version": "1.0.0",
                "estado": "activo",
                "documentacion": "/docs",
                "servicios": {
                    "redis": "conectado" if redis_service else "no disponible",
                    "mongodb": "deshabilitado temporalmente"
                }
            }
        )
    except Exception as e:
        logger.error(f"Error en endpoint root: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error interno del servidor",
                "mensaje": "No se pudo procesar la solicitud"
            }
        )


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    try:
        # Verificar Redis
        redis_ok = redis_service is not None
        
        return JSONResponse(
            status_code=200,
            content={
                "estado": "saludable" if redis_ok else "con_problemas",
                "servicios": {
                    "redis": "conectado" if redis_ok else "desconectado",
                    "mongodb": "deshabilitado temporalmente"
                }
            }
        )
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "estado": "error",
                "error": "Error en health check",
                "detalle": str(e)
            }
        )


@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba simple"""
    return JSONResponse(
        status_code=200,
        content={
            "mensaje": "¡Endpoint funcionando correctamente!",
            "timestamp": "2024-12-19T10:00:00Z"
        }
    )


@app.get("/api/v1/peliculas")
async def listar_peliculas():
    """Lista películas disponibles (versión simplificada)"""
    try:
        logger.info("🔍 Ejecutando listar_peliculas")
        
        peliculas = [
            {
                "id": "pel_001",
                "titulo": "Avengers: Endgame",
                "director": "Russo Brothers",
                "generos": ["accion", "aventura"],
                "duracion_minutos": 181,
                "clasificacion": "PG-13",
                "precio_base": 15000,
                "poster_url": "https://example.com/poster1.jpg"
            },
            {
                "id": "pel_002", 
                "titulo": "Toy Story 4",
                "director": "Josh Cooley",
                "generos": ["animacion", "familia"],
                "duracion_minutos": 100,
                "clasificacion": "G",
                "precio_base": 12000,
                "poster_url": "https://example.com/poster2.jpg"
            }
        ]
        
        response_data = {
            "peliculas": peliculas,
            "total": len(peliculas),
            "limite": 20,
            "offset": 0
        }
        
        logger.info(f"✅ Respuesta preparada con {len(peliculas)} películas")
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
    except Exception as e:
        logger.error(f"❌ Error en listar_peliculas: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error al obtener películas",
                "mensaje": str(e)
            }
        )


if __name__ == "__main__":
    print("🚀 Iniciando aplicación en modo estable...")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📖 Documentación en: http://localhost:8000/docs")
    print("🔍 Health check en: http://localhost:8000/health")
    print("🎬 Películas en: http://localhost:8000/api/v1/peliculas")
    print("⏹️  Presiona Ctrl+C para detener")
    
    uvicorn.run(
        "main_simple_stable:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Deshabilitar recarga automática
        log_level="info"
    ) 