"""
Controlador de Transacciones para el sistema de cine
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field
from datetime import datetime

from domain.entities.transaccion import MetodoPago, EstadoTransaccion
from use_cases.comprar_entrada_use_case import ComprarEntradaUseCase
from controllers.usuarios_controller import get_current_user
from services.email_service import email_service
from services.global_services import get_algorithms_service

router = APIRouter(prefix="/api/v1/transacciones", tags=["Transacciones"])

# DTOs para requests
class CompraEntradaRequest(BaseModel):
    funcion_id: str = Field(..., description="ID de la función")
    asientos: List[str] = Field(..., description="Lista de códigos de asientos")
    metodo_pago: MetodoPago = Field(..., description="Método de pago")
    datos_pago: Dict[str, Any] = Field(default_factory=dict, description="Datos adicionales del pago")
    codigo_promocion: str = Field(None, description="Código promocional (opcional)")


class CancelarTransaccionRequest(BaseModel):
    motivo: str = Field(None, description="Motivo de la cancelación")


# DTOs para responses
class TransaccionResponse(BaseModel):
    transaccion_id: str = Field(..., description="ID de la transacción")
    numero_factura: str = Field(..., description="Número de factura")
    estado: EstadoTransaccion = Field(..., description="Estado de la transacción")
    total: float = Field(..., description="Total de la transacción")
    asientos: List[str] = Field(..., description="Asientos comprados")
    fecha_vencimiento: str = Field(..., description="Fecha de vencimiento")
    resultado_pago: Dict[str, Any] = Field(..., description="Resultado del procesamiento de pago")
    resumen: Dict[str, Any] = Field(..., description="Resumen de la transacción")


class HistorialComprasResponse(BaseModel):
    transacciones: List[Dict[str, Any]] = Field(..., description="Lista de transacciones")
    total: int = Field(..., description="Total de transacciones")


@router.post("/comprar-entrada", response_model=TransaccionResponse)
async def comprar_entrada(
    request: CompraEntradaRequest,
    current_user: dict = Depends(get_current_user)
):
    """Comprar entradas para una función"""
    try:
        use_case = ComprarEntradaUseCase()
        
        # Agregar código promocional si existe
        if request.codigo_promocion:
            request.datos_pago["codigo_promocion"] = request.codigo_promocion
        
        # Agregar información del usuario
        request.datos_pago["ip_origen"] = "127.0.0.1"  # En producción obtener del request
        request.datos_pago["user_agent"] = "web"  # En producción obtener del request
        request.datos_pago["canal_venta"] = "web"
        
        resultado = await use_case.ejecutar(
            usuario_id=current_user["sub"],
            funcion_id=request.funcion_id,
            asientos=request.asientos,
            metodo_pago=request.metodo_pago,
            datos_pago=request.datos_pago
        )
        
        return TransaccionResponse(**resultado)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/historial", response_model=HistorialComprasResponse)
async def obtener_historial_compras(
    limit: int = 20,
    ordenar_por_fecha: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Obtener historial de compras del usuario con ordenamiento opcional"""
    try:
        use_case = ComprarEntradaUseCase()
        historial = await use_case.obtener_historial_compras(
            usuario_id=current_user["sub"],
            limit=limit
        )
        
        # Aplicar algoritmo de ordenamiento si se solicita
        algorithms_service = get_algorithms_service()
        if ordenar_por_fecha and algorithms_service and historial:
            print("🔄 Aplicando HeapSort para ordenar transacciones por fecha...")
            
            # Convertir a formato compatible con el algoritmo
            transacciones_formato = []
            for tx in historial:
                if isinstance(tx, dict):
                    transacciones_formato.append({
                        "id": tx.get("id", ""),
                        "fecha_transaccion": tx.get("fecha_creacion", ""),
                        "monto": tx.get("total", 0),
                        "estado": tx.get("estado", "")
                    })
                else:
                    # Si es un objeto, extraer datos
                    transacciones_formato.append({
                        "id": getattr(tx, "id", ""),
                        "fecha_transaccion": getattr(tx, "fecha_creacion", "").isoformat() if hasattr(tx, "fecha_creacion") else "",
                        "monto": getattr(tx, "total", 0),
                        "estado": getattr(tx, "estado", "")
                    })
            
            # Aplicar HeapSort
            transacciones_ordenadas = algorithms_service.heapsort_transacciones_fecha(transacciones_formato)
            print(f"✅ Transacciones ordenadas por fecha usando HeapSort")
            
            # Reconstruir historial con el orden correcto
            historial_ordenado = []
            for tx_ordenada in transacciones_ordenadas:
                # Encontrar la transacción original
                for tx_original in historial:
                    if isinstance(tx_original, dict):
                        if tx_original.get("id") == tx_ordenada["id"]:
                            historial_ordenado.append(tx_original)
                            break
                    else:
                        if getattr(tx_original, "id", "") == tx_ordenada["id"]:
                            historial_ordenado.append(tx_original)
                            break
            
            historial = historial_ordenado
        
        return HistorialComprasResponse(
            transacciones=historial,
            total=len(historial)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/{transaccion_id}/cancelar")
async def cancelar_transaccion(
    transaccion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancelar una transacción"""
    try:
        use_case = ComprarEntradaUseCase()
        
        resultado = await use_case.cancelar_transaccion(
            transaccion_id=transaccion_id,
            usuario_id=current_user["sub"]
        )
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{transaccion_id}")
async def obtener_transaccion(
    transaccion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener detalles de una transacción específica"""
    try:
        use_case = ComprarEntradaUseCase()
        
        # Obtener transacción del repositorio
        transaccion = await use_case.transaccion_repo.obtener_transaccion_por_id(transaccion_id)
        
        if not transaccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        # Verificar que el usuario es el propietario
        if transaccion.cliente_id != current_user["sub"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver esta transacción"
            )
        
        return {
            "id": transaccion.id,
            "numero_factura": transaccion.numero_factura,
            "fecha_creacion": transaccion.fecha_creacion.isoformat(),
            "fecha_actualizacion": transaccion.fecha_actualizacion.isoformat(),
            "estado": transaccion.estado,
            "funcion_id": transaccion.funcion_id,
            "pelicula_id": transaccion.pelicula_id,
            "asientos": transaccion.obtener_codigos_asientos(),
            "subtotal": transaccion.subtotal,
            "descuento_cliente": transaccion.descuento_cliente,
            "descuento_promocional": transaccion.descuento_promocional,
            "impuestos": transaccion.impuestos,
            "total": transaccion.total,
            "metodo_pago": transaccion.pago.metodo,
            "puede_cancelar": transaccion.puede_ser_cancelada(),
            "puede_reembolsar": transaccion.puede_ser_reembolsada(),
            "resumen": transaccion.generar_resumen()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/funciones/{funcion_id}/asientos-ocupados")
async def obtener_asientos_ocupados_funcion(funcion_id: str):
    """Obtener lista de asientos ocupados en una función"""
    try:
        use_case = ComprarEntradaUseCase()
        
        asientos_ocupados = await use_case.transaccion_repo.obtener_asientos_ocupados_funcion(funcion_id)
        
        return {
            "funcion_id": funcion_id,
            "asientos_ocupados": asientos_ocupados,
            "total_ocupados": len(asientos_ocupados)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/estadisticas/ventas")
async def obtener_estadisticas_ventas(
    fecha_inicio: str,
    fecha_fin: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener estadísticas de ventas (solo para administradores)"""
    try:
        # Verificar si el usuario es administrador (ejemplo)
        if not current_user.get("email", "").endswith("@admin.com"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver estadísticas"
            )
        
        from datetime import datetime
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
        fecha_fin_dt = datetime.fromisoformat(fecha_fin)
        
        use_case = ComprarEntradaUseCase()
        estadisticas = await use_case.transaccion_repo.obtener_estadisticas_ventas(
            fecha_inicio_dt, fecha_fin_dt
        )
        
        return {
            "periodo": {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            },
            "estadisticas": estadisticas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/procesar-correos")
async def procesar_cola_correos(
    batch_size: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Procesar cola de correos pendientes (solo administradores)"""
    try:
        # Verificar que el usuario es administrador (simulado)
        if not current_user.get("email", "").endswith("@admin.com"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden procesar correos"
            )
        
        # Procesar correos
        correos_procesados = await email_service.procesar_cola_correos(batch_size)
        
        return {
            "mensaje": f"Se procesaron {correos_procesados} correos",
            "correos_procesados": correos_procesados,
            "batch_size": batch_size,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando correos: {str(e)}"
        )


@router.get("/estadisticas/correos")
async def obtener_estadisticas_correos(
    current_user: dict = Depends(get_current_user)
):
    """Obtener estadísticas de correos enviados"""
    try:
        # Verificar que el usuario es administrador (simulado)
        if not current_user.get("email", "").endswith("@admin.com"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver estadísticas de correos"
            )
        
        estadisticas = await email_service.obtener_estadisticas_correos()
        
        return estadisticas
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas de correos: {str(e)}"
        ) 