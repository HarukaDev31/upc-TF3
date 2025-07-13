"""
Controlador de Usuarios para el sistema de cine
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field

from domain.entities.usuario import (
    UsuarioCreate, 
    UsuarioLogin, 
    UsuarioResponse, 
    LoginResponse, 
    RegistroResponse,
    TokenResponse
)
from domain.repositories.usuario_repository import UsuarioRepository
from services.global_services import get_mongodb_service
from services.auth_service import auth_service

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Obtener usuario actual desde token JWT"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido"
        )
    
    try:
        # Extraer token del header Authorization
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autorización inválido"
            )
        
        # Verificar token
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        
        return payload
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorización inválido"
        )


@router.post("/registro", response_model=RegistroResponse)
async def registrar_usuario(usuario_data: UsuarioCreate):
    """Registrar un nuevo usuario y devolver token JWT"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        usuario_creado = await usuario_repo.crear_usuario(usuario_data)
        
        if not usuario_creado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado o hubo un error en el registro"
            )
        
        # Generar token JWT
        token_data = {
            "sub": usuario_creado.id,
            "email": usuario_creado.email,
            "nombre": usuario_creado.nombre,
            "apellido": usuario_creado.apellido
        }
        
        access_token = auth_service.create_access_token(token_data)
        
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30  # minutos
        )
        
        return RegistroResponse(
            usuario=usuario_creado,
            token=token_response,
            mensaje="Usuario registrado exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login_usuario(login_data: UsuarioLogin):
    """Autenticar un usuario y devolver token JWT"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        usuario_autenticado = await usuario_repo.autenticar_usuario(
            login_data.email, 
            login_data.password
        )
        
        if not usuario_autenticado:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Generar token JWT
        token_data = {
            "sub": usuario_autenticado.id,
            "email": usuario_autenticado.email,
            "nombre": usuario_autenticado.nombre,
            "apellido": usuario_autenticado.apellido
        }
        
        access_token = auth_service.create_access_token(token_data)
        
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30  # minutos
        )
        
        return LoginResponse(
            usuario=usuario_autenticado,
            token=token_response,
            mensaje="Login exitoso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/me", response_model=UsuarioResponse)
async def obtener_usuario_actual(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual desde token JWT"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        usuario = await usuario_repo.obtener_usuario_por_id(current_user["sub"])
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: str):
    """Obtener información de un usuario"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        usuario = await usuario_repo.obtener_usuario_por_id(usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(skip: int = 0, limit: int = 100):
    """Listar usuarios con paginación"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        usuarios = await usuario_repo.listar_usuarios(skip=skip, limit=limit)
        
        return usuarios
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(usuario_id: str, datos_actualizacion: dict):
    """Actualizar datos de un usuario"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        usuario_actualizado = await usuario_repo.actualizar_usuario(usuario_id, datos_actualizacion)
        
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario_actualizado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete("/{usuario_id}")
async def desactivar_usuario(usuario_id: str):
    """Desactivar un usuario"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        usuario_repo = UsuarioRepository(mongodb_service.database)
        desactivado = await usuario_repo.desactivar_usuario(usuario_id)
        
        if not desactivado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return {"mensaje": "Usuario desactivado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        ) 