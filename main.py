from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import uvicorn

from config.settings import settings
from infrastructure.cache.redis_service import RedisService
from infrastructure.database.mongodb_service import MongoDBService


# Servicios globales
redis_service = RedisService()
mongodb_service = MongoDBService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando Sistema de Cine...")
    
    try:
        await redis_service.connect()
        print("✅ Conectado a Redis")
        
        await mongodb_service.connect()
        print("✅ Conectado a MongoDB")
        
        print("🎬 Sistema de Cine listo!")
        
    except Exception as e:
        print(f"❌ Error al inicializar: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Cerrando conexiones...")
    await redis_service.disconnect()
    await mongodb_service.disconnect()
    print("👋 ¡Hasta luego!")


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


# DTOs de entrada
from pydantic import BaseModel, Field
from typing import Optional

class CompraEntradaRequest(BaseModel):
    cliente_id: str = Field(..., description="ID del cliente")
    pelicula_id: str = Field(..., description="ID de la película")
    funcion_id: str = Field(..., description="ID de la función")
    asientos: List[str] = Field(..., description="Lista de códigos de asientos (ej: ['A5', 'A6'])")
    metodo_pago: str = Field(..., description="Método de pago")

class BuscarPeliculasRequest(BaseModel):
    texto: Optional[str] = Field(None, description="Texto a buscar")
    genero: Optional[str] = Field(None, description="Género de película")
    fecha: Optional[str] = Field(None, description="Fecha de función")
    limite: int = Field(default=20, le=100, description="Límite de resultados")


# Endpoints principales
@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "mensaje": "🎬 Sistema de Cine - API",
        "version": "1.0.0",
        "estado": "activo",
        "documentacion": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    try:
        # Verificar Redis
        redis_ok = await redis_service.exists("health_check") is not None
        
        # Verificar MongoDB  
        mongo_ok = mongodb_service.database is not None
        
        return {
            "estado": "saludable" if redis_ok and mongo_ok else "con_problemas",
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


@app.post("/api/v1/comprar-entrada")
async def comprar_entrada(request: CompraEntradaRequest):
    """
    Endpoint principal para comprar entradas
    Implementa el algoritmo optimizado de compra
    """
    try:
        # Aquí implementarías el algoritmo de compra
        # Por ahora devolvemos una respuesta simulada
        
        # Validaciones básicas
        if not request.asientos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe seleccionar al menos un asiento"
            )
        
        # Simular procesamiento
        resultado = {
            "transaccion_id": f"TRX_{request.cliente_id}_{request.funcion_id}",
            "estado": "confirmado",
            "asientos": request.asientos,
            "total": len(request.asientos) * 15000,  # Precio ejemplo
            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
            "numero_factura": f"CIN-{request.funcion_id}-001"
        }
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar compra: {str(e)}"
        )


@app.get("/api/v1/peliculas")
async def listar_peliculas(limite: int = 20, offset: int = 0):
    """Lista películas disponibles"""
    try:
        # Obtener desde MongoDB (simulado)
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
        
        return {
            "peliculas": peliculas[offset:offset+limite],
            "total": len(peliculas),
            "limite": limite,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener películas: {str(e)}"
        )


@app.get("/api/v1/peliculas/{pelicula_id}/funciones")
async def listar_funciones_pelicula(pelicula_id: str):
    """Lista funciones de una película específica"""
    try:
        # Simular funciones
        funciones = [
            {
                "id": "fun_001",
                "pelicula_id": pelicula_id,
                "fecha_hora_inicio": "2024-12-20T15:30:00",
                "fecha_hora_fin": "2024-12-20T18:30:00",
                "sala": {
                    "id": "sala_001",
                    "nombre": "Sala IMAX",
                    "tipo": "imax",
                    "capacidad_total": 200
                },
                "precio_base": 18000,
                "subtitulos": True,
                "idioma_audio": "español"
            },
            {
                "id": "fun_002",
                "pelicula_id": pelicula_id,
                "fecha_hora_inicio": "2024-12-20T19:00:00",
                "fecha_hora_fin": "2024-12-20T22:00:00",
                "sala": {
                    "id": "sala_002",
                    "nombre": "Sala VIP",
                    "tipo": "vip",
                    "capacidad_total": 100
                },
                "precio_base": 25000,
                "subtitulos": False,
                "idioma_audio": "español"
            }
        ]
        
        return {"funciones": funciones}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener funciones: {str(e)}"
        )


@app.get("/api/v1/funciones/{funcion_id}/asientos")
async def obtener_asientos_funcion(funcion_id: str):
    """Obtiene el mapa de asientos de una función"""
    try:
        # Simular estado de asientos usando Redis bitmap
        bitmap_key = f"sala:asientos:{funcion_id}"
        
        # En una implementación real, esto vendría del bitmap de Redis
        asientos_ocupados = ["A1", "A2", "B5", "C10"]
        
        # Generar mapa completo de asientos
        filas = ["A", "B", "C", "D", "E", "F", "G", "H"]
        asientos_por_fila = 15
        
        mapa_asientos = {}
        for fila in filas:
            mapa_asientos[fila] = []
            for num in range(1, asientos_por_fila + 1):
                codigo = f"{fila}{num}"
                mapa_asientos[fila].append({
                    "codigo": codigo,
                    "disponible": codigo not in asientos_ocupados,
                    "tipo": "vip" if fila in ["A", "B"] else "estandar",
                    "precio": 25000 if fila in ["A", "B"] else 18000
                })
        
        # Estadísticas
        total_asientos = len(filas) * asientos_por_fila
        ocupados = len(asientos_ocupados)
        disponibles = total_asientos - ocupados
        
        return {
            "funcion_id": funcion_id,
            "mapa_asientos": mapa_asientos,
            "estadisticas": {
                "total": total_asientos,
                "ocupados": ocupados,
                "disponibles": disponibles,
                "porcentaje_ocupacion": round((ocupados / total_asientos) * 100, 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asientos: {str(e)}"
        )


@app.post("/api/v1/buscar-peliculas")
async def buscar_peliculas(request: BuscarPeliculasRequest):
    """Búsqueda avanzada de películas"""
    try:
        # Implementar búsqueda con índices de texto de MongoDB
        resultados = [
            {
                "id": "pel_001",
                "titulo": "Spider-Man: No Way Home",
                "director": "Jon Watts",
                "generos": ["accion", "aventura"],
                "score": 0.95  # Score de relevancia del texto
            }
        ]
        
        return {
            "resultados": resultados,
            "criterios_busqueda": request.dict(),
            "total_encontrados": len(resultados)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )


@app.get("/api/v1/metricas/ranking-peliculas")
async def obtener_ranking_peliculas(limite: int = 10):
    """Obtiene el ranking de películas más vendidas desde Redis"""
    try:
        ranking = await redis_service.get_ranking_peliculas(limite)
        return {"ranking": ranking}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ranking: {str(e)}"
        )


@app.get("/api/v1/metricas/ocupacion/{funcion_id}")
async def obtener_ocupacion_sala(funcion_id: str):
    """Obtiene métricas de ocupación de una sala en tiempo real"""
    try:
        ocupacion = await redis_service.get_sala_ocupacion(funcion_id)
        return ocupacion
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ocupación: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 