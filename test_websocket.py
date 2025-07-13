#!/usr/bin/env python3
"""
Script de prueba para el WebSocket de selección de asientos
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket():
    """Prueba la funcionalidad del WebSocket"""
    
    # Configuración
    funcion_id = "fun_001"  # ID de función de prueba
    uri = f"ws://localhost:8000/ws/funciones/{funcion_id}/asientos"
    
    print(f"🔌 Conectando a WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al WebSocket")
            
            # Recibir mensaje de conexión
            connection_msg = await websocket.recv()
            connection_data = json.loads(connection_msg)
            print(f"📨 Mensaje de conexión: {connection_data}")
            
            # Simular selección de asientos
            test_messages = [
                {
                    "action": "select",
                    "asientos": ["A5", "A6"]
                },
                {
                    "action": "select", 
                    "asientos": ["B3"]
                },
                {
                    "action": "deselect",
                    "asientos": ["A5"]
                }
            ]
            
            for i, message in enumerate(test_messages):
                print(f"\n🔄 Enviando mensaje {i+1}: {message}")
                
                # Enviar mensaje
                await websocket.send(json.dumps(message))
                
                # Recibir confirmación
                response = await websocket.recv()
                response_data = json.loads(response)
                print(f"📨 Respuesta: {response_data}")
                
                # Esperar un poco entre mensajes
                await asyncio.sleep(2)
            
            # Mantener conexión abierta para recibir broadcasts
            print("\n👂 Esperando mensajes de otros usuarios...")
            print("💡 Abre otra terminal y ejecuta este script para simular otro usuario")
            
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    print(f"📨 Mensaje recibido: {data}")
            except asyncio.TimeoutError:
                print("⏰ Timeout - No más mensajes")
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ No se pudo conectar al WebSocket")
        print("💡 Asegúrate de que la API esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"💥 Error: {e}")

async def test_multiple_users():
    """Prueba múltiples usuarios conectados simultáneamente"""
    
    funcion_id = "fun_001"
    uri = f"ws://localhost:8000/ws/funciones/{funcion_id}/asientos"
    
    async def user_session(user_id: str):
        """Sesión de un usuario"""
        try:
            async with websockets.connect(uri) as websocket:
                print(f"👤 Usuario {user_id} conectado")
                
                # Recibir mensaje de conexión
                connection_msg = await websocket.recv()
                print(f"👤 {user_id}: Conectado")
                
                # Simular selecciones
                selections = [
                    (["A1", "A2"], "select"),
                    (["B5"], "select"),
                    (["A1"], "deselect")
                ]
                
                for asientos, action in selections:
                    message = {
                        "action": action,
                        "asientos": asientos
                    }
                    
                    print(f"👤 {user_id}: {action} {asientos}")
                    await websocket.send(json.dumps(message))
                    
                    # Recibir confirmación
                    response = await websocket.recv()
                    print(f"👤 {user_id}: Confirmado")
                    
                    await asyncio.sleep(1)
                
                # Escuchar broadcasts
                print(f"👤 {user_id}: Escuchando broadcasts...")
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        print(f"👤 {user_id}: Broadcast recibido - {data['type']}")
                except asyncio.TimeoutError:
                    print(f"👤 {user_id}: Timeout")
                    
        except Exception as e:
            print(f"👤 {user_id}: Error - {e}")
    
    # Crear múltiples usuarios
    users = ["user1", "user2", "user3"]
    tasks = [user_session(user_id) for user_id in users]
    
    print("🚀 Iniciando prueba con múltiples usuarios...")
    await asyncio.gather(*tasks)

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de WebSocket...")
    print("=" * 50)
    
    # Preguntar qué tipo de prueba ejecutar
    print("1. Prueba simple de un usuario")
    print("2. Prueba con múltiples usuarios")
    
    choice = input("Selecciona una opción (1 o 2): ").strip()
    
    if choice == "2":
        asyncio.run(test_multiple_users())
    else:
        asyncio.run(test_websocket())
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main() 