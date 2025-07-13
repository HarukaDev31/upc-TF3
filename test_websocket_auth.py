#!/usr/bin/env python3
"""
Script de prueba para WebSocket con autenticación JWT
"""

import asyncio
import websockets
import json
import sys
import os

# Agregar el directorio actual al path
sys.path.append('.')

from services.auth_service import auth_service
from domain.entities.usuario import UsuarioCreate
from domain.repositories.usuario_repository import UsuarioRepository
from infrastructure.database.mongodb_service import MongoDBService


async def test_websocket_with_auth():
    """Probar WebSocket con autenticación JWT"""
    print("🧪 Probando WebSocket con autenticación JWT...")
    
    try:
        # 1. Crear un usuario de prueba
        print("\n1. Creando usuario de prueba...")
        mongodb_service = MongoDBService()
        await mongodb_service.connect()
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        
        # Datos de prueba
        usuario_data = UsuarioCreate(
            email="websocket@test.com",
            nombre="WebSocket",
            apellido="Test",
            telefono="+573001234567",
            password="password123"
        )
        
        # Crear usuario
        usuario_creado = await usuario_repo.crear_usuario(usuario_data)
        
        if not usuario_creado:
            print("   ❌ Error al crear usuario de prueba")
            return
        
        print(f"   ✅ Usuario creado: {usuario_creado.nombre} {usuario_creado.apellido}")
        print(f"   ID: {usuario_creado.id}")
        
        # 2. Generar token JWT
        print("\n2. Generando token JWT...")
        token_data = {
            "sub": usuario_creado.id,
            "email": usuario_creado.email,
            "nombre": usuario_creado.nombre,
            "apellido": usuario_creado.apellido
        }
        
        token = auth_service.create_access_token(token_data)
        print(f"   ✅ Token generado: {token[:50]}...")
        
        # 3. Conectar al WebSocket con token
        print("\n3. Conectando al WebSocket...")
        funcion_id = "fun_001"
        ws_url = f"ws://localhost:8000/ws/funciones/{funcion_id}/asientos?token={token}"
        
        async with websockets.connect(ws_url) as websocket:
            print("   ✅ Conexión WebSocket establecida")
            
            # 4. Recibir mensaje de conexión
            print("\n4. Recibiendo mensaje de conexión...")
            response = await websocket.recv()
            data = json.loads(response)
            
            print(f"   📨 Mensaje recibido: {json.dumps(data, indent=2)}")
            
            if data.get("type") == "connection_established":
                print("   ✅ Conexión establecida correctamente")
                print(f"   👤 Usuario: {data.get('user_info', {}).get('nombre')} {data.get('user_info', {}).get('apellido')}")
                print(f"   🆔 User ID: {data.get('user_id')}")
            else:
                print("   ❌ Error en mensaje de conexión")
                return
            
            # 5. Enviar selección de asientos
            print("\n5. Enviando selección de asientos...")
            message = {
                "action": "select",
                "asientos": ["A1", "A2", "B3"]
            }
            
            await websocket.send(json.dumps(message))
            print(f"   📤 Mensaje enviado: {json.dumps(message)}")
            
            # 6. Recibir confirmación
            response = await websocket.recv()
            data = json.loads(response)
            
            print(f"   📨 Confirmación recibida: {json.dumps(data, indent=2)}")
            
            if data.get("type") == "selection_confirmed":
                print("   ✅ Selección confirmada correctamente")
            else:
                print("   ❌ Error en confirmación de selección")
            
            # 7. Enviar deselección
            print("\n6. Enviando deselección de asientos...")
            message = {
                "action": "deselect",
                "asientos": ["A1", "A2"]
            }
            
            await websocket.send(json.dumps(message))
            print(f"   📤 Mensaje enviado: {json.dumps(message)}")
            
            # 8. Recibir confirmación de deselección
            response = await websocket.recv()
            data = json.loads(response)
            
            print(f"   📨 Confirmación recibida: {json.dumps(data, indent=2)}")
            
            if data.get("type") == "selection_confirmed":
                print("   ✅ Deselección confirmada correctamente")
            else:
                print("   ❌ Error en confirmación de deselección")
            
            print("\n✅ Prueba de WebSocket con autenticación completada exitosamente!")
            
        # Limpiar - eliminar usuario de prueba
        if mongodb_service.database:
            await mongodb_service.database.usuarios.delete_one({"email": "websocket@test.com"})
            print("   🧹 Usuario de prueba eliminado")
        
    except Exception as e:
        print(f"   ❌ Error en prueba de WebSocket: {e}")
    finally:
        await mongodb_service.disconnect()


async def test_websocket_without_auth():
    """Probar WebSocket sin autenticación (debe fallar)"""
    print("\n🧪 Probando WebSocket sin autenticación (debe fallar)...")
    
    try:
        funcion_id = "fun_001"
        ws_url = f"ws://localhost:8000/ws/funciones/{funcion_id}/asientos"
        
        async with websockets.connect(ws_url) as websocket:
            print("   ❌ Error: Se conectó sin autenticación (no debería pasar)")
            
    except Exception as e:
        print(f"   ✅ Correcto: Conexión rechazada sin autenticación: {str(e)[:100]}...")


async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de WebSocket con autenticación JWT...")
    
    # Probar WebSocket con autenticación
    await test_websocket_with_auth()
    
    # Probar WebSocket sin autenticación
    await test_websocket_without_auth()
    
    print("\n🎉 Todas las pruebas completadas!")


if __name__ == "__main__":
    asyncio.run(main()) 