#!/usr/bin/env python3
"""
Script de prueba para verificar tanto la API como el servicio WebSocket
"""

import asyncio
import json
import websockets
import time
import random
import requests
from datetime import datetime

class ServicesTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8001"
        self.client_id = f"test_client_{random.randint(1000, 9999)}"
        
    def test_api_health(self):
        """Probar health check de la API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Health: {data}")
                return True
            else:
                print(f"❌ API Health falló: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error en API Health: {e}")
            return False
    
    def test_websocket_health(self):
        """Probar health check del WebSocket"""
        try:
            response = requests.get(f"{self.websocket_url.replace('ws://', 'http://')}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ WebSocket Health: {data}")
                return True
            else:
                print(f"❌ WebSocket Health falló: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error en WebSocket Health: {e}")
            return False
    
    def test_api_endpoints(self):
        """Probar endpoints de la API"""
        print("\n🔍 Probando endpoints de la API...")
        
        endpoints = [
            "/",
            "/docs",
            "/api/v1/peliculas",
            "/api/v1/funciones"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint}: OK")
                else:
                    print(f"⚠️  {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
    
    async def test_websocket_connection(self):
        """Probar conexión WebSocket"""
        print(f"\n🔌 Probando conexión WebSocket como {self.client_id}...")
        
        try:
            uri = f"{self.websocket_url}/ws/{self.client_id}"
            websocket = await websockets.connect(uri)
            print("✅ Conexión WebSocket establecida")
            
            # Unirse a sala de prueba
            join_message = {
                "type": "join_room",
                "room_id": "test_room"
            }
            await websocket.send(json.dumps(join_message))
            print("📝 Enviado: join_room")
            
            # Esperar respuesta
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📨 Recibido: {data}")
            
            # Seleccionar asiento
            select_message = {
                "type": "select_seat",
                "room_id": "test_room",
                "seat_id": "A1",
                "user_info": {
                    "name": f"Usuario {self.client_id}",
                    "email": f"user{self.client_id}@test.com"
                }
            }
            await websocket.send(json.dumps(select_message))
            print("📝 Enviado: select_seat")
            
            # Esperar respuesta
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📨 Recibido: {data}")
            
            # Liberar asiento
            release_message = {
                "type": "release_seat",
                "room_id": "test_room",
                "seat_id": "A1"
            }
            await websocket.send(json.dumps(release_message))
            print("📝 Enviado: release_seat")
            
            # Esperar respuesta
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📨 Recibido: {data}")
            
            await websocket.close()
            print("✅ Prueba WebSocket completada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error en WebSocket: {e}")
            return False
    
    async def test_multiple_websocket_clients(self):
        """Probar múltiples clientes WebSocket"""
        print(f"\n👥 Probando múltiples clientes WebSocket...")
        
        clients = []
        tasks = []
        
        # Crear 3 clientes
        for i in range(3):
            client_id = f"multi_client_{i}_{random.randint(1000, 9999)}"
            task = asyncio.create_task(self.test_single_websocket_client(client_id))
            tasks.append(task)
        
        # Esperar que todos terminen
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        print(f"✅ {success_count}/3 clientes WebSocket funcionaron correctamente")
        
        return success_count == 3
    
    async def test_single_websocket_client(self, client_id):
        """Probar un solo cliente WebSocket"""
        try:
            uri = f"{self.websocket_url}/ws/{client_id}"
            websocket = await websockets.connect(uri)
            
            # Unirse a sala
            join_message = {
                "type": "join_room",
                "room_id": "multi_test_room"
            }
            await websocket.send(json.dumps(join_message))
            
            # Esperar confirmación
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get("type") == "room_joined":
                # Seleccionar asiento
                seat_id = f"{chr(65 + random.randint(0, 5))}{random.randint(1, 10)}"
                select_message = {
                    "type": "select_seat",
                    "room_id": "multi_test_room",
                    "seat_id": seat_id,
                    "user_info": {
                        "name": f"Usuario {client_id}",
                        "email": f"user{client_id}@test.com"
                    }
                }
                await websocket.send(json.dumps(select_message))
                
                # Esperar confirmación
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data.get("type") == "seat_selected":
                    await websocket.close()
                    return True
            
            await websocket.close()
            return False
            
        except Exception as e:
            print(f"❌ Error en cliente {client_id}: {e}")
            return False
    
    async def run_full_test(self):
        """Ejecutar prueba completa"""
        print("🚀 Iniciando prueba completa de servicios...")
        print("=" * 50)
        
        # Probar health checks
        api_ok = self.test_api_health()
        websocket_ok = self.test_websocket_health()
        
        if not api_ok or not websocket_ok:
            print("❌ Health checks fallaron. Verifica que los servicios estén corriendo.")
            return False
        
        # Probar endpoints de API
        self.test_api_endpoints()
        
        # Probar WebSocket
        websocket_connection_ok = await self.test_websocket_connection()
        
        if not websocket_connection_ok:
            print("❌ Prueba de WebSocket falló.")
            return False
        
        # Probar múltiples clientes
        multiple_clients_ok = await self.test_multiple_websocket_clients()
        
        print("\n" + "=" * 50)
        if multiple_clients_ok:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        else:
            print("⚠️  Algunas pruebas fallaron.")
        
        return multiple_clients_ok

async def main():
    """Función principal"""
    tester = ServicesTester()
    
    try:
        success = await tester.run_full_test()
        if success:
            print("\n✅ Servicios funcionando correctamente")
            print("📊 URLs disponibles:")
            print("   - API: http://localhost:8000")
            print("   - WebSocket: ws://localhost:8001/ws/{client_id}")
            print("   - API Docs: http://localhost:8000/docs")
            print("   - WebSocket Health: http://localhost:8001/health")
        else:
            print("\n❌ Algunos servicios no están funcionando correctamente")
            print("💡 Verifica que los servicios estén corriendo:")
            print("   docker-compose logs api")
            print("   docker-compose ps")
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Pruebas interrumpidas por usuario")
    except Exception as e:
        print(f"❌ Error: {e}") 