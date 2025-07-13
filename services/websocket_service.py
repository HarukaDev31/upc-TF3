"""
Servicio de WebSocket para manejo de selección de asientos en tiempo real
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from pydantic import BaseModel

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/websocket.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis123")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Configuración del servicio WebSocket
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 8001))
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", "0.0.0.0")

class WebSocketService:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.room_connections: Dict[str, Set[str]] = {}
        self.temporary_selections: Dict[str, Dict] = {}
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect_redis(self):
        """Conectar a Redis"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Conectado a Redis exitosamente")
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            self.redis_client = None

    async def disconnect_redis(self):
        """Desconectar de Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Desconectado de Redis")

    async def connect(self, websocket: WebSocket, client_id: str):
        """Conectar un cliente WebSocket"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Cliente {client_id} conectado. Total de conexiones: {len(self.active_connections)}")

    async def disconnect(self, client_id: str):
        """Desconectar un cliente WebSocket"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        # Remover de todas las salas
        for room_id in list(self.room_connections.keys()):
            if client_id in self.room_connections[room_id]:
                self.room_connections[room_id].remove(client_id)
                if not self.room_connections[room_id]:
                    del self.room_connections[room_id]
                    
        # Limpiar selecciones temporales del cliente
        await self.clear_client_selections(client_id)
        logger.info(f"Cliente {client_id} desconectado. Total de conexiones: {len(self.active_connections)}")

    async def join_room(self, client_id: str, room_id: str):
        """Unir un cliente a una sala"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(client_id)
        logger.info(f"Cliente {client_id} unido a sala {room_id}")

    async def leave_room(self, client_id: str, room_id: str):
        """Sacar un cliente de una sala"""
        if room_id in self.room_connections and client_id in self.room_connections[room_id]:
            self.room_connections[room_id].remove(client_id)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
            logger.info(f"Cliente {client_id} salió de sala {room_id}")

    async def send_personal_message(self, message: str, client_id: str):
        """Enviar mensaje personal a un cliente"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje a {client_id}: {e}")
                await self.disconnect(client_id)

    async def broadcast_to_room(self, message: str, room_id: str, exclude_client: Optional[str] = None):
        """Enviar mensaje a todos los clientes en una sala"""
        if room_id in self.room_connections:
            for client_id in self.room_connections[room_id]:
                if client_id != exclude_client:
                    await self.send_personal_message(message, client_id)

    async def select_seat(self, client_id: str, room_id: str, seat_id: str, user_info: dict):
        """Seleccionar un asiento temporalmente"""
        selection_key = f"selection:{room_id}:{seat_id}"
        client_key = f"client:{client_id}"
        
        # Guardar selección en Redis con expiración de 5 minutos
        selection_data = {
            "client_id": client_id,
            "seat_id": seat_id,
            "room_id": room_id,
            "user_info": user_info,
            "timestamp": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        
        if self.redis_client:
            await self.redis_client.setex(
                selection_key,
                300,  # 5 minutos
                json.dumps(selection_data)
            )
            await self.redis_client.setex(
                client_key,
                300,
                json.dumps({"room_id": room_id, "seat_id": seat_id})
            )
        
        # Guardar en memoria también
        self.temporary_selections[selection_key] = selection_data
        
        # Notificar a otros clientes en la sala
        notification = {
            "type": "seat_selected",
            "seat_id": seat_id,
            "room_id": room_id,
            "client_id": client_id,
            "user_info": user_info
        }
        
        await self.broadcast_to_room(json.dumps(notification), room_id, client_id)
        logger.info(f"Asiento {seat_id} seleccionado por {client_id} en sala {room_id}")

    async def release_seat(self, client_id: str, room_id: str, seat_id: str):
        """Liberar un asiento"""
        selection_key = f"selection:{room_id}:{seat_id}"
        client_key = f"client:{client_id}"
        
        # Verificar que el asiento fue seleccionado por este cliente
        if self.redis_client:
            selection_data = await self.redis_client.get(selection_key)
            if selection_data:
                data = json.loads(selection_data)
                if data.get("client_id") == client_id:
                    await self.redis_client.delete(selection_key)
                    await self.redis_client.delete(client_key)
        
        # Limpiar de memoria
        if selection_key in self.temporary_selections:
            del self.temporary_selections[selection_key]
        
        # Notificar a otros clientes
        notification = {
            "type": "seat_released",
            "seat_id": seat_id,
            "room_id": room_id,
            "client_id": client_id
        }
        
        await self.broadcast_to_room(json.dumps(notification), room_id, client_id)
        logger.info(f"Asiento {seat_id} liberado por {client_id} en sala {room_id}")

    async def clear_client_selections(self, client_id: str):
        """Limpiar todas las selecciones de un cliente"""
        if self.redis_client:
            # Buscar todas las selecciones del cliente
            pattern = f"selection:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                selection_data = await self.redis_client.get(key)
                if selection_data:
                    data = json.loads(selection_data)
                    if data.get("client_id") == client_id:
                        await self.redis_client.delete(key)
                        room_id = data.get("room_id")
                        seat_id = data.get("seat_id")
                        
                        # Notificar liberación
                        notification = {
                            "type": "seat_released",
                            "seat_id": seat_id,
                            "room_id": room_id,
                            "client_id": client_id
                        }
                        
                        if room_id:
                            await self.broadcast_to_room(json.dumps(notification), room_id, client_id)
            
            # Limpiar clave del cliente
            client_key = f"client:{client_id}"
            await self.redis_client.delete(client_key)
        
        # Limpiar de memoria
        keys_to_remove = [k for k, v in self.temporary_selections.items() if v.get("client_id") == client_id]
        for key in keys_to_remove:
            del self.temporary_selections[key]

    async def get_room_selections(self, room_id: str):
        """Obtener todas las selecciones activas de una sala"""
        selections = []
        
        if self.redis_client:
            pattern = f"selection:{room_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                selection_data = await self.redis_client.get(key)
                if selection_data:
                    data = json.loads(selection_data)
                    # Verificar si no ha expirado
                    expires_at = datetime.fromisoformat(data.get("expires_at", "1970-01-01T00:00:00"))
                    if expires_at > datetime.now():
                        selections.append(data)
        
        return selections

    async def cleanup_expired_selections(self):
        """Limpiar selecciones expiradas"""
        if self.redis_client:
            pattern = f"selection:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                selection_data = await self.redis_client.get(key)
                if selection_data:
                    data = json.loads(selection_data)
                    expires_at = datetime.fromisoformat(data.get("expires_at", "1970-01-01T00:00:00"))
                    
                    if expires_at <= datetime.now():
                        await self.redis_client.delete(key)
                        logger.info(f"Selección expirada eliminada: {key}")

# Instancia global del servicio
websocket_service = WebSocketService()

# Crear aplicación FastAPI
app = FastAPI(
    title="Cinemax WebSocket Service",
    description="Servicio WebSocket para selección de asientos en tiempo real",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Evento de inicio del servicio"""
    await websocket_service.connect_redis()
    logger.info("Servicio WebSocket iniciado")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre del servicio"""
    await websocket_service.disconnect_redis()
    logger.info("Servicio WebSocket cerrado")

@app.get("/health")
async def health_check():
    """Endpoint de salud del servicio"""
    return {
        "status": "healthy",
        "service": "websocket",
        "active_connections": len(websocket_service.active_connections),
        "active_rooms": len(websocket_service.room_connections),
        "redis_connected": websocket_service.redis_client is not None
    }

@app.get("/stats")
async def get_stats():
    """Obtener estadísticas del servicio"""
    return {
        "active_connections": len(websocket_service.active_connections),
        "active_rooms": len(websocket_service.room_connections),
        "temporary_selections": len(websocket_service.temporary_selections),
        "clients": list(websocket_service.active_connections.keys()),
        "rooms": list(websocket_service.room_connections.keys())
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Endpoint principal de WebSocket"""
    await websocket_service.connect(websocket, client_id)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "join_room":
                room_id = message.get("room_id")
                await websocket_service.join_room(client_id, room_id)
                
                # Enviar confirmación
                response = {
                    "type": "room_joined",
                    "room_id": room_id,
                    "client_id": client_id
                }
                await websocket_service.send_personal_message(json.dumps(response), client_id)
                
                # Enviar selecciones actuales de la sala
                selections = await websocket_service.get_room_selections(room_id)
                if selections:
                    response = {
                        "type": "current_selections",
                        "selections": selections
                    }
                    await websocket_service.send_personal_message(json.dumps(response), client_id)
                
            elif message_type == "leave_room":
                room_id = message.get("room_id")
                await websocket_service.leave_room(client_id, room_id)
                
                response = {
                    "type": "room_left",
                    "room_id": room_id,
                    "client_id": client_id
                }
                await websocket_service.send_personal_message(json.dumps(response), client_id)
                
            elif message_type == "select_seat":
                room_id = message.get("room_id")
                seat_id = message.get("seat_id")
                user_info = message.get("user_info", {})
                
                await websocket_service.select_seat(client_id, room_id, seat_id, user_info)
                
                response = {
                    "type": "seat_selected",
                    "seat_id": seat_id,
                    "room_id": room_id,
                    "client_id": client_id
                }
                await websocket_service.send_personal_message(json.dumps(response), client_id)
                
            elif message_type == "release_seat":
                room_id = message.get("room_id")
                seat_id = message.get("seat_id")
                
                await websocket_service.release_seat(client_id, room_id, seat_id)
                
                response = {
                    "type": "seat_released",
                    "seat_id": seat_id,
                    "room_id": room_id,
                    "client_id": client_id
                }
                await websocket_service.send_personal_message(json.dumps(response), client_id)
                
            elif message_type == "ping":
                response = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket_service.send_personal_message(json.dumps(response), client_id)
                
    except WebSocketDisconnect:
        logger.info(f"Cliente {client_id} desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket para cliente {client_id}: {e}")
    finally:
        await websocket_service.disconnect(client_id)

@app.get("/room/{room_id}/selections")
async def get_room_selections(room_id: str):
    """Obtener selecciones de una sala específica"""
    selections = await websocket_service.get_room_selections(room_id)
    return {
        "room_id": room_id,
        "selections": selections,
        "count": len(selections)
    }

def run_websocket_service():
    """Función para ejecutar el servicio WebSocket"""
    uvicorn.run(
        "services.websocket_service:app",
        host=WEBSOCKET_HOST,
        port=WEBSOCKET_PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    run_websocket_service() 