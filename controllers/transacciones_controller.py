from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel, Field
from services.global_services import get_mongodb_service
from infrastructure.cache.redis_service import RedisService
from use_cases.comprar_entrada_use_case import ComprarEntradaUseCase

router = APIRouter(prefix="/api/v1/transacciones", tags=["Transacciones"])

# DTOs
class CompraEntradaRequest(BaseModel):
    cliente_id: str = Field(..., description="ID del cliente")
    pelicula_id: str = Field(..., description="ID de la película")
    funcion_id: str = Field(..., description="ID de la función")
    asientos: List[str] = Field(..., description="Lista de códigos de asientos (ej: ['A5', 'A6'])")
    metodo_pago: str = Field(..., description="Método de pago")

class CompraEntradaResponse(BaseModel):
    transaccion_id: str
    estado: str
    asientos: List[str]
    total: float
    qr_code: str
    numero_factura: str

@router.post("/comprar-entrada", response_model=CompraEntradaResponse)
async def comprar_entrada(request: CompraEntradaRequest):
    """
    Endpoint principal para comprar entradas
    Implementa el algoritmo optimizado de compra
    """
    try:
        # Validaciones básicas
        if not request.asientos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe seleccionar al menos un asiento"
            )
        
        # Usar el caso de uso para procesar la compra
        use_case = ComprarEntradaUseCase()
        resultado = await use_case.ejecutar(request)
        
        return CompraEntradaResponse(**resultado)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar compra: {str(e)}"
        )

@router.get("/{transaccion_id}", response_model=dict)
async def obtener_transaccion(transaccion_id: str):
    """Obtiene información de una transacción específica"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        transaccion = await mongodb_service.obtener_transaccion(transaccion_id)
        
        if not transaccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        return transaccion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener transacción: {str(e)}"
        )

@router.get("/cliente/{cliente_id}", response_model=dict)
async def listar_transacciones_cliente(
    cliente_id: str,
    limite: int = 20
):
    """Lista las transacciones de un cliente específico"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        transacciones = await mongodb_service.listar_transacciones_cliente(cliente_id, limite)
        
        return {
            "cliente_id": cliente_id,
            "transacciones": transacciones,
            "total": len(transacciones)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener transacciones: {str(e)}"
        )

@router.post("/{transaccion_id}/cancelar")
async def cancelar_transaccion(transaccion_id: str):
    """Cancela una transacción y libera los asientos"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = RedisService()
        
        # Obtener transacción
        transaccion = await mongodb_service.obtener_transaccion(transaccion_id)
        if not transaccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        if transaccion.get("estado") == "cancelada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La transacción ya está cancelada"
            )
        
        # Liberar asientos en Redis
        funcion_id = transaccion.get("funcion_id")
        asientos = transaccion.get("asientos", [])
        
        if funcion_id and asientos:
            await redis_service.liberar_asientos(funcion_id, asientos)
        
        # Actualizar estado en MongoDB
        await mongodb_service.actualizar_transaccion(
            transaccion_id, 
            {"estado": "cancelada", "fecha_cancelacion": "2024-12-20T10:00:00Z"}
        )
        
        return {
            "transaccion_id": transaccion_id,
            "estado": "cancelada",
            "mensaje": "Transacción cancelada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar transacción: {str(e)}"
        ) 