"""
Controlador de Selecciones de Asientos para el sistema de cine
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from domain.entities.seleccion_asiento import (
    SeleccionAsientoCreate, 
    SeleccionAsientoUpdate,
    SeleccionAsientoResponse,
    HistorialSeleccion
)
from domain.repositories.seleccion_asiento_repository import SeleccionAsientoRepository
from services.global_services import get_mongodb_service

router = APIRouter(prefix="/api/v1/selecciones", tags=["Selecciones de Asientos"])


class SeleccionResponse(BaseModel):
    """Respuesta de selección"""
    seleccion: SeleccionAsientoResponse
    mensaje: str = Field(..., description="Mensaje de confirmación")


@router.post("/", response_model=SeleccionResponse)
async def crear_seleccion(seleccion_data: SeleccionAsientoCreate):
    """Crear una nueva selección de asiento"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        seleccion_creada = await seleccion_repo.crear_seleccion(seleccion_data)
        
        if not seleccion_creada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El asiento ya está seleccionado o hubo un error en la selección"
            )
        
        return SeleccionResponse(
            seleccion=seleccion_creada,
            mensaje="Asiento seleccionado exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{seleccion_id}", response_model=SeleccionAsientoResponse)
async def obtener_seleccion(seleccion_id: str):
    """Obtener información de una selección"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        seleccion = await seleccion_repo.obtener_seleccion_por_id(seleccion_id)
        
        if not seleccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selección no encontrada"
            )
        
        return seleccion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/funcion/{funcion_id}", response_model=List[SeleccionAsientoResponse])
async def obtener_selecciones_funcion(funcion_id: str):
    """Obtener todas las selecciones de una función"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        selecciones = await seleccion_repo.obtener_selecciones_por_funcion(funcion_id)
        
        return selecciones
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/usuario/{usuario_id}", response_model=List[SeleccionAsientoResponse])
async def obtener_selecciones_usuario(usuario_id: str):
    """Obtener todas las selecciones de un usuario"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        selecciones = await seleccion_repo.obtener_selecciones_por_usuario(usuario_id)
        
        return selecciones
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.put("/{seleccion_id}", response_model=SeleccionAsientoResponse)
async def actualizar_seleccion(seleccion_id: str, datos_actualizacion: SeleccionAsientoUpdate):
    """Actualizar estado de una selección"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        seleccion_actualizada = await seleccion_repo.actualizar_seleccion(seleccion_id, datos_actualizacion)
        
        if not seleccion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selección no encontrada"
            )
        
        return seleccion_actualizada
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/{seleccion_id}/confirmar")
async def confirmar_seleccion(seleccion_id: str):
    """Confirmar una selección"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        confirmada = await seleccion_repo.confirmar_seleccion(seleccion_id)
        
        if not confirmada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selección no encontrada"
            )
        
        return {"mensaje": "Selección confirmada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/{seleccion_id}/cancelar")
async def cancelar_seleccion(seleccion_id: str):
    """Cancelar una selección"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        cancelada = await seleccion_repo.cancelar_seleccion(seleccion_id)
        
        if not cancelada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selección no encontrada"
            )
        
        return {"mensaje": "Selección cancelada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/funcion/{funcion_id}/historial", response_model=HistorialSeleccion)
async def obtener_historial_funcion(funcion_id: str):
    """Obtener historial completo de selecciones de una función"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        historial = await seleccion_repo.obtener_historial_funcion(funcion_id)
        
        return historial
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/limpiar-expiradas")
async def limpiar_selecciones_expiradas():
    """Limpiar selecciones temporales expiradas"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
        limpiadas = await seleccion_repo.limpiar_selecciones_expiradas()
        
        return {
            "mensaje": f"Se limpiaron {limpiadas} selecciones expiradas",
            "selecciones_limpiadas": limpiadas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        ) 