from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import uvicorn

from config.settings import settings
from services.global_services import set_redis_service, set_mongodb_service, set_algorithms_service, get_redis_service, get_mongodb_service, get_algorithms_service

# Importar controladores
from controllers.peliculas_controller import router as peliculas_router
from controllers.funciones_controller import router as funciones_router
from controllers.transacciones_controller import router as transacciones_router
from controllers.metricas_controller import router as metricas_router
from controllers.websocket_controller import router as websocket_router
from controllers.usuarios_controller import router as usuarios_router
from controllers.selecciones_controller import router as selecciones_router
from controllers.algoritmos_controller import router as algoritmos_router


# Servicios globales - Inicializar como None por ahora
redis_service = None
mongodb_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando Sistema de Cine...")
    
    try:
        # Intentar conectar a Redis
        try:
            from infrastructure.cache.redis_service import RedisService
            global redis_service
            redis_service = RedisService()
            await redis_service.connect()
            set_redis_service(redis_service)
            print("✅ Conectado a Redis")
        except Exception as e:
            print(f"⚠️  No se pudo conectar a Redis: {e}")
            print("📝 Continuando sin Redis...")
        
        # Intentar conectar a MongoDB
        try:
            from infrastructure.database.mongodb_service import MongoDBService
            global mongodb_service
            mongodb_service = MongoDBService()
            await mongodb_service.connect()
            set_mongodb_service(mongodb_service)
            print("✅ Conectado a MongoDB")
        except Exception as e:
            print(f"⚠️  No se pudo conectar a MongoDB: {e}")
            print("📝 Continuando sin MongoDB...")
        
        # Inicializar servicio de algoritmos
        try:
            from services.algorithms_service import algorithms_service
            set_algorithms_service(algorithms_service)
            print("✅ Servicio de algoritmos inicializado")
        except Exception as e:
            print(f"⚠️  No se pudo inicializar algoritmos: {e}")
            print("📝 Continuando sin algoritmos...")
        
        print("🎬 Sistema de Cine listo!")
        
    except Exception as e:
        print(f"❌ Error al inicializar: {e}")
        print("📝 Continuando con funcionalidad limitada...")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando conexiones...")
    if redis_service:
        await redis_service.disconnect()
    if mongodb_service:
        await mongodb_service.disconnect()
    print("👋 ¡Hasta luego!")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.project_name,
    description="Sistema avanzado de venta de entradas de cine con Redis y MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS completamente abierto para pruebas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Cambiar a False para evitar conflictos
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir routers de controladores
app.include_router(peliculas_router)
app.include_router(funciones_router)
app.include_router(transacciones_router)
app.include_router(metricas_router)
app.include_router(websocket_router)
app.include_router(usuarios_router)
app.include_router(selecciones_router)
app.include_router(algoritmos_router)

# Ruta de test para CORS
@app.get("/test-cors")
async def test_cors():
    return {"mensaje": "CORS funcionando correctamente"}


# Endpoints principales
@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "mensaje": "🎬 Sistema de Cine - API",
        "version": "1.0.0",
        "estado": "activo",
        "documentacion": "/docs",
        "servicios": {
            "redis": "conectado" if get_redis_service() else "no disponible",
            "mongodb": "conectado" if get_mongodb_service() else "no disponible"
        }
    }


@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Maneja las peticiones OPTIONS para CORS preflight"""
    return {
        "message": "CORS preflight handled",
        "path": full_path
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    try:
        # Verificar Redis
        redis_ok = get_redis_service() is not None
        
        # Verificar MongoDB  
        mongo_ok = get_mongodb_service() is not None
        
        return {
            "estado": "saludable" if redis_ok or mongo_ok else "con_problemas",
            "servicios": {
                "redis": "conectado" if redis_ok else "desconectado",
                "mongodb": "conectado" if mongo_ok else "desconectado"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error en health check: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 