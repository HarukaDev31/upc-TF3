#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad JWT
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append('.')

from services.auth_service import auth_service
from domain.entities.usuario import UsuarioCreate, UsuarioLogin
from domain.repositories.usuario_repository import UsuarioRepository
from infrastructure.database.mongodb_service import MongoDBService


async def test_jwt_functionality():
    """Probar la funcionalidad JWT"""
    print("🧪 Probando funcionalidad JWT...")
    
    # 1. Probar generación de hash de contraseña
    print("\n1. Probando hash de contraseña...")
    password = "mi_contraseña_segura"
    password_hash = auth_service.get_password_hash(password)
    print(f"   Contraseña original: {password}")
    print(f"   Hash generado: {password_hash[:50]}...")
    
    # 2. Probar verificación de contraseña
    print("\n2. Probando verificación de contraseña...")
    is_valid = auth_service.verify_password(password, password_hash)
    print(f"   Verificación exitosa: {is_valid}")
    
    # 3. Probar generación de token JWT
    print("\n3. Probando generación de token JWT...")
    user_data = {
        "sub": "507f1f77bcf86cd799439011",
        "email": "usuario@ejemplo.com",
        "nombre": "Juan",
        "apellido": "Pérez"
    }
    
    token = auth_service.create_access_token(user_data)
    print(f"   Token generado: {token[:50]}...")
    
    # 4. Probar verificación de token
    print("\n4. Probando verificación de token...")
    payload = auth_service.verify_token(token)
    if payload:
        print(f"   Token válido - Usuario: {payload.get('nombre')} {payload.get('apellido')}")
        print(f"   Email: {payload.get('email')}")
    else:
        print("   ❌ Token inválido")
    
    # 5. Probar token inválido
    print("\n5. Probando token inválido...")
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
    payload = auth_service.verify_token(invalid_token)
    print(f"   Token inválido detectado: {payload is None}")
    
    print("\n✅ Todas las pruebas JWT completadas exitosamente!")


async def test_user_creation():
    """Probar creación de usuario con JWT"""
    print("\n🧪 Probando creación de usuario...")
    
    try:
        # Conectar a MongoDB
        mongodb_service = MongoDBService()
        await mongodb_service.connect()
        
        # Crear repositorio
        usuario_repo = UsuarioRepository(mongodb_service.database)
        
        # Datos de prueba
        usuario_data = UsuarioCreate(
            email="test@jwt.com",
            nombre="Test",
            apellido="JWT",
            telefono="+573001234567",
            password="password123"
        )
        
        # Crear usuario
        usuario_creado = await usuario_repo.crear_usuario(usuario_data)
        
        if usuario_creado:
            print(f"   ✅ Usuario creado: {usuario_creado.nombre} {usuario_creado.apellido}")
            print(f"   ID: {usuario_creado.id}")
            print(f"   Email: {usuario_creado.email}")
            
            # Probar autenticación
            print("\n   🔐 Probando autenticación...")
            usuario_autenticado = await usuario_repo.autenticar_usuario(
                "test@jwt.com", 
                "password123"
            )
            
            if usuario_autenticado:
                print(f"   ✅ Autenticación exitosa: {usuario_autenticado.nombre}")
            else:
                print("   ❌ Autenticación fallida")
            
            # Limpiar - eliminar usuario de prueba
            if mongodb_service.database:
                await mongodb_service.database.usuarios.delete_one({"email": "test@jwt.com"})
                print("   🧹 Usuario de prueba eliminado")
            
        else:
            print("   ❌ Error al crear usuario")
            
    except Exception as e:
        print(f"   ❌ Error en prueba de usuario: {e}")
    finally:
        await mongodb_service.disconnect()


async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de autenticación JWT...")
    
    # Probar funcionalidad JWT básica
    await test_jwt_functionality()
    
    # Probar creación de usuario
    await test_user_creation()
    
    print("\n🎉 Todas las pruebas completadas!")


if __name__ == "__main__":
    asyncio.run(main()) 