from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from services.global_services import get_mongodb_service, get_redis_service
from infrastructure.cache.redis_service import RedisService

router = APIRouter(prefix="/api/v1/funciones", tags=["Funciones"])

# DTOs
class AsientoInfo(BaseModel):
    codigo: str
    disponible: bool
    tipo: str
    precio: float

class MapaAsientosResponse(BaseModel):
    funcion_id: str
    mapa_asientos: Dict[str, List[AsientoInfo]]
    estadisticas: Dict[str, Any]

@router.get("/{funcion_id}/asientos", response_model=MapaAsientosResponse)
async def obtener_asientos_funcion(funcion_id: str):
    """Obtiene el mapa de asientos de una función con estado en tiempo real"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = get_redis_service()
        
        # Verificar que la función existe
        funcion = await mongodb_service.obtener_funcion(funcion_id)
        if not funcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Función no encontrada"
            )
        
        # Obtener asientos ocupados desde Redis
        asientos_ocupados = []
        if redis_service:
            try:
                asientos_ocupados = await redis_service.get_asientos_ocupados(funcion_id)
            except Exception as e:
                print(f"⚠️  Error obteniendo asientos ocupados desde Redis: {e}")
                asientos_ocupados = []
        else:
            print("⚠️  Redis no disponible, usando lista vacía de asientos ocupados")
            asientos_ocupados = []
        
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
                
                mapa_asientos[fila].append(AsientoInfo(
                    codigo=codigo,
                    disponible=disponible,
                    tipo=tipo,
                    precio=precio
                ))
        
        # Estadísticas
        total_asientos = len(filas) * asientos_por_fila
        ocupados = len(asientos_ocupados)
        disponibles = total_asientos - ocupados
        
        return MapaAsientosResponse(
            funcion_id=funcion_id,
            mapa_asientos=mapa_asientos,
            estadisticas={
                "total": total_asientos,
                "ocupados": ocupados,
                "disponibles": disponibles,
                "porcentaje_ocupacion": round((ocupados / total_asientos) * 100, 2)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asientos: {str(e)}"
        )

@router.get("/{funcion_id}", response_model=dict)
async def obtener_funcion(funcion_id: str):
    """Obtiene información detallada de una función"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        funcion = await mongodb_service.obtener_funcion(funcion_id)
        
        if not funcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Función no encontrada"
            )
        
        # Obtener información de la película
        pelicula = await mongodb_service.obtener_pelicula(funcion.get("pelicula_id"))
        
        return {
            "funcion": funcion,
            "pelicula": pelicula
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener función: {str(e)}"
        )

@router.post("/{funcion_id}/reservar-asientos")
async def reservar_asientos_temporales(
    funcion_id: str,
    asientos: List[str],
    tiempo_reserva: int = 300  # 5 minutos por defecto
):
    """Reserva asientos temporalmente para evitar conflictos"""
    try:
        redis_service = get_redis_service()
        
        if not redis_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de Redis no disponible"
            )
        
        # Verificar disponibilidad
        asientos_ocupados = await redis_service.get_asientos_ocupados(funcion_id)
        asientos_disponibles = [a for a in asientos if a not in asientos_ocupados]
        
        if len(asientos_disponibles) != len(asientos):
            asientos_no_disponibles = [a for a in asientos if a in asientos_ocupados]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asientos no disponibles: {asientos_no_disponibles}"
            )
        
        # Crear reserva temporal
        reserva_id = await redis_service.crear_reserva_temporal(
            funcion_id, asientos_disponibles, tiempo_reserva
        )
        
        return {
            "reserva_id": reserva_id,
            "asientos_reservados": asientos_disponibles,
            "tiempo_expiracion": tiempo_reserva,
            "mensaje": "Asientos reservados temporalmente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reservar asientos: {str(e)}"
        ) 