"""
Controlador WebSocket para manejo de selección de asientos en tiempo real
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Query
from pydantic import BaseModel, Field
from services.websocket_service import manager
from services.global_services import get_mongodb_service
from services.auth_service import auth_service
from domain.repositories.seleccion_asiento_repository import SeleccionAsientoRepository
from domain.entities.seleccion_asiento import SeleccionAsientoCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

# DTOs para mensajes WebSocket
class SeatSelectionMessage(BaseModel):
    action: str = Field(..., description="Acción: 'select' o 'deselect'")
    asientos: list = Field(..., description="Lista de códigos de asientos")

class WebSocketResponse(BaseModel):
    type: str = Field(..., description="Tipo de mensaje")
    data: Dict[str, Any] = Field(..., description="Datos del mensaje")
    timestamp: str = Field(..., description="Timestamp del mensaje")

async def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verificar token JWT y devolver payload"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido"
        )
    
    try:
        # Verificar token
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        
        return payload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error al verificar token: {str(e)}"
        )

@router.websocket("/ws/funciones/{funcion_id}/asientos")
async def websocket_endpoint(
    websocket: WebSocket, 
    funcion_id: str,
    token: str = Query(..., description="Token JWT de autenticación")
):
    """Endpoint WebSocket para selección de asientos en tiempo real (requiere autenticación)"""
    
    try:
        # Verificar token JWT
        user_payload = await verify_jwt_token(token)
        user_id = user_payload["sub"]  # ID real del usuario de la BD
        
        # Conectar al WebSocket
        await manager.connect_for_function(websocket, funcion_id, user_id)
        
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
            "user_info": {
                "nombre": user_payload.get("nombre"),
                "apellido": user_payload.get("apellido"),
                "email": user_payload.get("email")
            },
            "message": "Conectado a selección de asientos",
            "timestamp": "2024-12-20T10:00:00Z"
        }))
        
        logger.info(f"WebSocket conectado: {user_id} ({user_payload.get('nombre')} {user_payload.get('apellido')}) -> {funcion_id}")
        
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
                
                # Guardar en base de datos si es selección
                if action == "select":
                    mongodb_service = get_mongodb_service()
                    if mongodb_service:
                        seleccion_repo = SeleccionAsientoRepository(mongodb_service.database)
                        for asiento in asientos:
                            seleccion_data = SeleccionAsientoCreate(
                                funcion_id=funcion_id,
                                usuario_id=user_id,
                                asiento_id=asiento,
                                estado="temporal"
                            )
                            await seleccion_repo.crear_seleccion(seleccion_data)
                
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
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Mensaje JSON inválido",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }))
                except:
                    break
            except WebSocketDisconnect:
                logger.info(f"WebSocket desconectado: {user_id} -> {funcion_id}")
                break
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket: {e}")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Error interno del servidor",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }))
                except:
                    break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: {user_id} -> {funcion_id}")
        manager.disconnect_from_function(funcion_id, user_id)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect_from_function(funcion_id, user_id)

@router.get("/api/v1/funciones/{funcion_id}/selecciones-activas")
async def obtener_selecciones_activas(funcion_id: str):
    """Obtiene las selecciones activas para una función (para debugging)"""
    try:
        active_selections = await manager.get_active_selections(funcion_id)
        
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

@router.websocket("/ws/{client_id}")
async def websocket_client_endpoint(websocket: WebSocket, client_id: str):
    """Endpoint WebSocket genérico para clientes (compatibilidad)"""
    
    try:
        # Conectar al WebSocket
        await manager.connect(websocket, client_id)
        
        # Enviar mensaje de conexión exitosa
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Conectado al WebSocket",
            "timestamp": "2024-12-20T10:00:00Z"
        }))
        
        logger.info(f"WebSocket cliente conectado: {client_id}")
        
        # Loop principal para recibir mensajes
        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == "join_room":
                    room_id = message.get("room_id")
                    await manager.join_room(client_id, room_id)
                    
                    # Enviar confirmación
                    response = {
                        "type": "room_joined",
                        "room_id": room_id,
                        "client_id": client_id
                    }
                    await manager.send_personal_message(json.dumps(response), client_id)
                    
                elif message_type == "leave_room":
                    room_id = message.get("room_id")
                    await manager.leave_room(client_id, room_id)
                    
                    response = {
                        "type": "room_left",
                        "room_id": room_id,
                        "client_id": client_id
                    }
                    await manager.send_personal_message(json.dumps(response), client_id)
                    
                elif message_type == "send_message":
                    room_id = message.get("room_id")
                    message_text = message.get("message", "")
                    
                    # Enviar mensaje a todos en la sala
                    await manager.broadcast_to_room(
                        json.dumps({
                            "type": "message",
                            "room_id": room_id,
                            "client_id": client_id,
                            "message": message_text,
                            "timestamp": "2024-12-20T10:00:00Z"
                        }),
                        room_id
                    )
                    
                else:
                    # Mensaje no reconocido
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": "Tipo de mensaje no reconocido",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }), client_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Mensaje JSON inválido",
                    "timestamp": "2024-12-20T10:00:00Z"
                }), client_id)
            except WebSocketDisconnect:
                logger.info(f"WebSocket cliente desconectado: {client_id}")
                break
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket cliente: {e}")
                try:
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": "Error interno del servidor",
                        "timestamp": "2024-12-20T10:00:00Z"
                    }), client_id)
                except:
                    break
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket cliente desconectado: {client_id}")
    except Exception as e:
        logger.error(f"Error en WebSocket cliente: {e}")
    finally:
        await manager.disconnect(client_id) 