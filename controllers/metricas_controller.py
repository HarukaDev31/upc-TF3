from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any
from services.global_services import get_mongodb_service
from infrastructure.cache.redis_service import RedisService

router = APIRouter(prefix="/api/v1/metricas", tags=["Métricas"])

@router.get("/ranking-peliculas")
async def obtener_ranking_peliculas(limite: int = Query(10, le=50, description="Límite de resultados")):
    """Obtiene el ranking de películas más vendidas desde Redis y MongoDB"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = RedisService()
        
        # Obtener ranking desde MongoDB
        ranking_mongo = await mongodb_service.obtener_peliculas_mas_vendidas(limite)
        
        # Obtener ranking desde Redis (si está disponible)
        ranking_redis = await redis_service.get_ranking_peliculas(limite)
        
        return {
            "ranking_mongodb": ranking_mongo,
            "ranking_redis": ranking_redis,
            "total_peliculas": len(ranking_mongo)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ranking: {str(e)}"
        )

@router.get("/ocupacion/{funcion_id}")
async def obtener_ocupacion_sala(funcion_id: str):
    """Obtiene métricas de ocupación de una sala en tiempo real"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = RedisService()
        
        # Verificar que la función existe
        funcion = await mongodb_service.obtener_funcion(funcion_id)
        if not funcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Función no encontrada"
            )
        
        # Obtener ocupación desde Redis
        ocupacion_redis = await redis_service.get_sala_ocupacion(funcion_id)
        
        # Obtener transacciones confirmadas desde MongoDB
        transacciones = await mongodb_service.listar_transacciones_funcion(funcion_id)
        
        return {
            "funcion_id": funcion_id,
            "ocupacion_redis": ocupacion_redis,
            "transacciones_confirmadas": len(transacciones),
            "funcion": funcion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ocupación: {str(e)}"
        )

@router.get("/ventas/periodo")
async def obtener_metricas_ventas(
    fecha_inicio: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    """Obtiene métricas de ventas en un período específico"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        metricas = await mongodb_service.obtener_metricas_ventas(fecha_inicio, fecha_fin)
        
        return {
            "periodo": {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            },
            "metricas": metricas
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas: {str(e)}"
        )

@router.get("/dashboard/resumen")
async def obtener_resumen_dashboard():
    """Obtiene un resumen general para el dashboard"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = RedisService()
        
        # Métricas básicas
        total_peliculas = await mongodb_service.contar_peliculas_activas()
        total_funciones_hoy = await mongodb_service.contar_funciones_hoy()
        total_transacciones_hoy = await mongodb_service.contar_transacciones_hoy()
        
        # Ocupación promedio
        ocupacion_promedio = await redis_service.get_ocupacion_promedio()
        
        return {
            "resumen": {
                "peliculas_activas": total_peliculas,
                "funciones_hoy": total_funciones_hoy,
                "transacciones_hoy": total_transacciones_hoy,
                "ocupacion_promedio": ocupacion_promedio
            },
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen: {str(e)}"
        ) 