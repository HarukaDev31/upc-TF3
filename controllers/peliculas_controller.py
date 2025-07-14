from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from services.global_services import get_mongodb_service
from infrastructure.cache.redis_service import RedisService

router = APIRouter(prefix="/api/v1/peliculas", tags=["Películas"])

# DTOs
class BuscarPeliculasRequest(BaseModel):
    texto: Optional[str] = Field(None, description="Texto a buscar")
    genero: Optional[str] = Field(None, description="Género de película")
    fecha: Optional[str] = Field(None, description="Fecha de función")
    limite: int = Field(default=20, le=100, description="Límite de resultados")

class PeliculaResponse(BaseModel):
    id: str
    titulo: str
    director: str
    generos: List[str]
    duracion_minutos: int
    clasificacion: str
    precio_base: float
    poster_url: Optional[str] = None

@router.get("/", response_model=dict)
async def listar_peliculas(
    limite: int = Query(20, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación")
):
    """Lista películas disponibles con paginación"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        # Obtener películas desde MongoDB
        filtros = {"activa": True}
        peliculas = await mongodb_service.buscar_peliculas(filtros, limite + offset)
        
        # Aplicar paginación
        peliculas_paginadas = peliculas[offset:offset + limite]
        
        return {
            "peliculas": peliculas_paginadas,
            "total": len(peliculas),
            "limite": limite,
            "offset": offset,
            "paginas": (len(peliculas) + limite - 1) // limite
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener películas: {str(e)}"
        )

@router.get("/{pelicula_id}", response_model=dict)
async def obtener_pelicula(pelicula_id: str):
    """Obtiene una película específica por ID"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        pelicula = await mongodb_service.obtener_pelicula(pelicula_id)
        
        if not pelicula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Película no encontrada"
            )
        
        return pelicula
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener película: {str(e)}"
        )

@router.post("/buscar", response_model=dict)
async def buscar_peliculas(request: BuscarPeliculasRequest):
    """Búsqueda avanzada de películas con filtros"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        print(f"🔍 Búsqueda iniciada - Texto: '{request.texto}', Género: '{request.genero}', Límite: {request.limite}")
        
        # Construir filtros
        filtros = {"activa": True}
        
        if request.genero and request.genero.strip():
            filtros["generos"] = {"$in": [request.genero]}
            print(f"📝 Filtro de género aplicado: {request.genero}")
        
        # Búsqueda por texto si se proporciona
        if request.texto and request.texto.strip():
            print(f"🔤 Búsqueda de texto: '{request.texto}'")
            try:
                resultados = await mongodb_service.buscar_peliculas_texto(request.texto, request.limite)
                print(f"✅ Búsqueda de texto completada - {len(resultados)} resultados")
            except Exception as e:
                print(f"⚠️ Error en búsqueda de texto: {e}")
                # Fallback a búsqueda normal si falla la búsqueda de texto
                resultados = await mongodb_service.buscar_peliculas(filtros, request.limite)
                print(f"🔄 Fallback a búsqueda normal - {len(resultados)} resultados")
        else:
            print(f"📋 Búsqueda sin texto - usando filtros básicos")
            resultados = await mongodb_service.buscar_peliculas(filtros, request.limite)
            print(f"✅ Búsqueda normal completada - {len(resultados)} resultados")
        
        # Log de resultados para debug
        if resultados:
            print(f"📊 Primeros 3 resultados:")
            for i, pelicula in enumerate(resultados[:3]):
                print(f"  {i+1}. {pelicula.get('titulo', 'Sin título')} - ID: {pelicula.get('_id', 'Sin ID')}")
        else:
            print(f"❌ No se encontraron resultados")
        
        return {
            "resultados": resultados,
            "criterios_busqueda": request.dict(),
            "total_encontrados": len(resultados)
        }
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )

@router.get("/{pelicula_id}/funciones", response_model=dict)
async def listar_funciones_pelicula(pelicula_id: str):
    """Lista funciones de una película específica"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        # Verificar que la película existe
        pelicula = await mongodb_service.obtener_pelicula(pelicula_id)
        if not pelicula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Película no encontrada"
            )
        
        # Obtener funciones de la película
        funciones = await mongodb_service.listar_funciones_pelicula(pelicula_id)
        
        return {
            "pelicula": pelicula,
            "funciones": funciones,
            "total_funciones": len(funciones)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener funciones: {str(e)}"
        ) 