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


@app.get("/api/v1/peliculas-minimal")
async def peliculas_minimal():
    """Endpoint mínima para aislar el problema"""
    logger.info("🔍 Ejecutando peliculas_minimal")
    
    # Respuesta directa sin JSONResponse
    return {"test": "ok", "mensaje": "Endpoint mínima funcionando"}


@app.get("/api/v1/peliculas-simple")
async def listar_peliculas_simple():
    """Endpoint simple para probar películas"""
    try:
        logger.info("🔍 Ejecutando listar_peliculas_simple")
        
        # Respuesta mínima
        response_data = {
            "mensaje": "Películas cargadas correctamente",
            "peliculas": [
                {
                    "id": "pel_001",
                    "titulo": "Avengers: Endgame"
                }
            ]
        }
        
        logger.info(f"✅ Respuesta preparada: {response_data}")
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
    except Exception as e:
        logger.error(f"❌ Error en listar_peliculas_simple: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error interno",
                "mensaje": str(e)
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


@app.get("/api/v1/funciones/{funcion_id}/asientos")
async def obtener_asientos_funcion(funcion_id: str):
    """Obtiene el mapa de asientos de una función (versión simplificada)"""
    try:
        # Simular asientos ocupados
        asientos_ocupados = ["A1", "A2", "B5", "C10"]
        
        # Generar mapa completo de asientos
        filas = ["A", "B", "C", "D", "E", "F", "G", "H"]
        asientos_por_fila = 15
        
        mapa_asientos = {}
        for fila in filas:
            mapa_asientos[fila] = []
            for num in range(1, asientos_por_fila + 1):
                codigo = f"{fila}{num}"
                disponible = codigo not in asientos_ocupados
                tipo = "vip" if fila in ["A", "B"] else "estandar"
                precio = 25000 if fila in ["A", "B"] else 18000
                
                mapa_asientos[fila].append({
                    "codigo": codigo,
                    "disponible": disponible,
                    "tipo": tipo,
                    "precio": precio
                })
        
        # Estadísticas
        total_asientos = len(filas) * asientos_por_fila
        ocupados = len(asientos_ocupados)
        disponibles = total_asientos - ocupados
        
        return JSONResponse(
            status_code=200,
            content={
                "funcion_id": funcion_id,
                "mapa_asientos": mapa_asientos,
                "estadisticas": {
                    "total": total_asientos,
                    "ocupados": ocupados,
                    "disponibles": disponibles,
                    "porcentaje_ocupacion": round((ocupados / total_asientos) * 100, 2)
                }
            }
        )
    except Exception as e:
        logger.error(f"❌ Error en obtener_asientos_funcion: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error al obtener asientos",
                "mensaje": "No se pudo cargar el mapa de asientos"
            }
        )


if __name__ == "__main__":
    uvicorn.run(
        "main_simple_fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 