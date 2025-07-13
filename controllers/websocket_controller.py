"""
Controlador WebSocket para manejo de selección de asientos en tiempo real
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from pydantic import BaseModel, Field
from services.websocket_service import manager
from services.global_services import get_mongodb_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

# DTOs para mensajes WebSocket
class SeatSelectionMessage(BaseModel):
    action: str = Field(..., description="Acción: 'select' o 'deselect'")
    asientos: list = Field(..., description="Lista de códigos de asientos")
    user_id: str = Field(..., description="ID del usuario")

class WebSocketResponse(BaseModel):
    type: str = Field(..., description="Tipo de mensaje")
    data: Dict[str, Any] = Field(..., description="Datos del mensaje")
    timestamp: str = Field(..., description="Timestamp del mensaje")

@router.websocket("/ws/funciones/{funcion_id}/asientos")
async def websocket_endpoint(websocket: WebSocket, funcion_id: str):
    """Endpoint WebSocket para selección de asientos en tiempo real"""
    
    # Generar un user_id temporal (en producción usar autenticación)
    import uuid
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    try:
        # Conectar al WebSocket
        await manager.connect(websocket, funcion_id, user_id)
        
        # Verificar que la función existe
        mongodb_service = get_mongodb_service()
        if mongodb_service:
            funcion = await mongodb_service.obtener_funcion(funcion_id)
            if not funcion:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Función no encontrada",
                    "timestamp": "2024-12-20T10:00:00Z"
                }))
                await websocket.close()
                return
        
        # Enviar mensaje de conexión exitosa
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "funcion_id": funcion_id,
            "user_id": user_id,
            "message": "Conectado a selección de asientos",
            "timestamp": "2024-12-20T10:00:00Z"
        }))
        
        logger.info(f"WebSocket conectado: {user_id} -> {funcion_id}")
        
        # Loop principal para recibir mensajes
        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Validar estructura del mensaje
                if "action" not in message or "asientos" not in message:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Formato de mensaje inválido",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }))
                    continue
                
                action = message["action"]
                asientos = message["asientos"]
                
                # Validar acción
                if action not in ["select", "deselect"]:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Acción inválida. Use 'select' o 'deselect'",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }))
                    continue
                
                # Validar asientos
                if not isinstance(asientos, list) or not asientos:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Debe especificar al menos un asiento",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }))
                    continue
                
                # Procesar selección/deselección
                await manager.handle_seat_selection(funcion_id, user_id, asientos, action)
                
                # Confirmar al usuario
                await websocket.send_text(json.dumps({
                    "type": "selection_confirmed",
                    "action": action,
                    "asientos": asientos,
                    "user_id": user_id,
                    "funcion_id": funcion_id,
                    "timestamp": "2024-12-20T10:00:00Z"
                }))
                
                logger.info(f"Usuario {user_id} {action} asientos {asientos} en función {funcion_id}")
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Mensaje JSON inválido",
                    "timestamp": "2024-12-20T10:00:00Z"
                }))
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Error interno del servidor",
                    "timestamp": "2024-12-20T10:00:00Z"
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: {user_id} -> {funcion_id}")
        manager.disconnect(funcion_id, user_id)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect(funcion_id, user_id)

@router.get("/api/v1/funciones/{funcion_id}/selecciones-activas")
async def obtener_selecciones_activas(funcion_id: str):
    """Obtiene las selecciones activas para una función (para debugging)"""
    try:
        active_selections = manager.get_active_selections(funcion_id)
        
        return {
            "funcion_id": funcion_id,
            "selecciones_activas": active_selections,
            "total_selecciones": len(active_selections),
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener selecciones activas: {str(e)}"
        )

@router.post("/api/v1/funciones/{funcion_id}/limpiar-selecciones")
async def limpiar_selecciones_funcion(funcion_id: str):
    """Limpia todas las selecciones temporales de una función (para debugging)"""
    try:
        if funcion_id in manager.temporary_selections:
            del manager.temporary_selections[funcion_id]
        
        return {
            "funcion_id": funcion_id,
            "message": "Selecciones limpiadas exitosamente",
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar selecciones: {str(e)}"
        ) 