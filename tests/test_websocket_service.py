#!/usr/bin/env python3
"""
Script de prueba para el servicio WebSocket independiente
"""

import asyncio
import json
import websockets
import time
import random
from datetime import datetime

class WebSocketTester:
    def __init__(self, server_url="ws://localhost:8001"):
        self.server_url = server_url
        self.client_id = f"test_client_{random.randint(1000, 9999)}"
        self.websocket = None
        self.room_id = "test_room_123"
        self.selected_seats = set()
        self.other_selections = set()
        
    async def connect(self):
        """Conectar al servicio WebSocket"""
        try:
            uri = f"{self.server_url}/ws/{self.client_id}"
            print(f"Conectando a {uri}...")
            
            self.websocket = await websockets.connect(uri)
            print(f"✅ Conectado exitosamente como {self.client_id}")
            
            # Unirse a sala de prueba
            await self.join_room()
            
            return True
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    async def join_room(self):
        """Unirse a una sala"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
        message = {
            "type": "join_room",
            "room_id": self.room_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"📝 Enviado: {message}")
    
    async def leave_room(self):
        """Salir de la sala"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
        message = {
            "type": "leave_room",
            "room_id": self.room_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"📝 Enviado: {message}")
    
    async def select_seat(self, seat_id, user_info=None):
        """Seleccionar un asiento"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
        if user_info is None:
            user_info = {
                "name": f"Usuario {self.client_id}",
                "email": f"user{self.client_id}@test.com"
            }
        
        message = {
            "type": "select_seat",
            "room_id": self.room_id,
            "seat_id": seat_id,
            "user_info": user_info
        }
        await self.websocket.send(json.dumps(message))
        print(f"📝 Enviado: {message}")
        self.selected_seats.add(seat_id)
    
    async def release_seat(self, seat_id):
        """Liberar un asiento"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
        message = {
            "type": "release_seat",
            "room_id": self.room_id,
            "seat_id": seat_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"📝 Enviado: {message}")
        self.selected_seats.discard(seat_id)
    
    async def ping(self):
        """Enviar ping"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
        message = {
            "type": "ping"
        }
        await self.websocket.send(json.dumps(message))
        print(f"📝 Enviado: {message}")
    
    async def listen_for_messages(self):
        """Escuchar mensajes del servidor"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"📨 Recibido: {data}")
                
                # Procesar mensajes
                await self.handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Conexión cerrada por el servidor")
        except Exception as e:
            print(f"❌ Error recibiendo mensaje: {e}")
    
    async def handle_message(self, data):
        """Manejar mensajes recibidos"""
        message_type = data.get("type")
        
        if message_type == "room_joined":
            print(f"✅ Unido a sala: {data.get('room_id')}")
            
        elif message_type == "room_left":
            print(f"👋 Salido de sala: {data.get('room_id')}")
            
        elif message_type == "seat_selected":
            seat_id = data.get("seat_id")
            client_id = data.get("client_id")
            
            if client_id != self.client_id:
                self.other_selections.add(seat_id)
                print(f"🪑 Asiento {seat_id} seleccionado por {client_id}")
            else:
                print(f"✅ Asiento {seat_id} seleccionado exitosamente")
                
        elif message_type == "seat_released":
            seat_id = data.get("seat_id")
            client_id = data.get("client_id")
            
            if client_id != self.client_id:
                self.other_selections.discard(seat_id)
                print(f"🪑 Asiento {seat_id} liberado por {client_id}")
            else:
                print(f"✅ Asiento {seat_id} liberado exitosamente")
                
        elif message_type == "current_selections":
            selections = data.get("selections", [])
            print(f"📋 Selecciones actuales en la sala: {len(selections)}")
            for selection in selections:
                print(f"  - {selection.get('seat_id')} por {selection.get('client_id')}")
                
        elif message_type == "pong":
            timestamp = data.get("timestamp")
            print(f"🏓 Pong recibido: {timestamp}")
            
        else:
            print(f"❓ Mensaje desconocido: {message_type}")
    
    async def run_test_scenario(self):
        """Ejecutar escenario de prueba completo"""
        print(f"\n🎬 Iniciando escenario de prueba para {self.client_id}")
        print("=" * 50)
        
        # Conectar
        if not await self.connect():
            return
        
        # Escuchar mensajes en background
        listen_task = asyncio.create_task(self.listen_for_messages())
        
        try:
            # Esperar un poco para recibir selecciones actuales
            await asyncio.sleep(2)
            
            # Seleccionar algunos asientos
            seats_to_select = ["A1", "B3", "C5"]
            for seat in seats_to_select:
                await self.select_seat(seat)
                await asyncio.sleep(1)
            
            # Esperar un poco
            await asyncio.sleep(3)
            
            # Liberar algunos asientos
            seats_to_release = ["A1", "C5"]
            for seat in seats_to_release:
                await self.release_seat(seat)
                await asyncio.sleep(1)
            
            # Enviar ping
            await self.ping()
            await asyncio.sleep(1)
            
            # Esperar un poco más para ver otros mensajes
            await asyncio.sleep(5)
            
            # Salir de la sala
            await self.leave_room()
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error en escenario de prueba: {e}")
        
        finally:
            # Cerrar conexión
            if self.websocket:
                await self.websocket.close()
                print("🔌 Conexión cerrada")
            
            # Cancelar tarea de escucha
            listen_task.cancel()
    
    async def run_interactive_mode(self):
        """Modo interactivo para pruebas manuales"""
        print(f"\n🎮 Modo interactivo para {self.client_id}")
        print("Comandos disponibles:")
        print("  select <asiento> - Seleccionar asiento")
        print("  release <asiento> - Liberar asiento")
        print("  ping - Enviar ping")
        print("  leave - Salir de sala")
        print("  quit - Salir")
        print("=" * 50)
        
        if not await self.connect():
            return
        
        # Escuchar mensajes en background
        listen_task = asyncio.create_task(self.listen_for_messages())
        
        try:
            while True:
                command = input(f"[{self.client_id}] > ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "select" and len(command) > 1:
                    seat_id = command[1]
                    await self.select_seat(seat_id)
                    
                elif cmd == "release" and len(command) > 1:
                    seat_id = command[1]
                    await self.release_seat(seat_id)
                    
                elif cmd == "ping":
                    await self.ping()
                    
                elif cmd == "leave":
                    await self.leave_room()
                    
                elif cmd == "quit":
                    break
                    
                else:
                    print("❌ Comando inválido")
                    
        except KeyboardInterrupt:
            print("\n👋 Interrumpido por usuario")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
            listen_task.cancel()

async def test_multiple_clients():
    """Probar múltiples clientes simultáneamente"""
    print("\n👥 Probando múltiples clientes...")
    
    clients = []
    tasks = []
    
    # Crear 3 clientes
    for i in range(3):
        client = WebSocketTester()
        clients.append(client)
        task = asyncio.create_task(client.run_test_scenario())
        tasks.append(task)
        
        # Esperar un poco entre clientes
        await asyncio.sleep(2)
    
    # Esperar que todos terminen
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n✅ Prueba de múltiples clientes completada")

async def test_health_endpoints():
    """Probar endpoints HTTP del servicio"""
    print("\n🏥 Probando endpoints de salud...")
    print("⚠️  Nota: Esta función requiere aiohttp. Instala con: pip install aiohttp")
    print("   O usa curl directamente:")
    print("   curl http://localhost:8001/health")
    print("   curl http://localhost:8001/stats")

async def main():
    """Función principal"""
    import sys
    
    print("🚀 Iniciando pruebas del servicio WebSocket")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "interactive":
            client = WebSocketTester()
            await client.run_interactive_mode()
            
        elif mode == "multi":
            await test_multiple_clients()
            
        elif mode == "health":
            await test_health_endpoints()
            
        else:
            print("❌ Modo inválido. Usar: interactive, multi, o health")
    else:
        # Modo por defecto: un cliente con escenario de prueba
        client = WebSocketTester()
        await client.run_test_scenario()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Pruebas interrumpidas por usuario")
    except Exception as e:
        print(f"❌ Error en pruebas: {e}") 