"""
Entidad Usuario para el sistema de cine
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class Usuario(BaseModel):
    """Entidad Usuario"""
    id: Optional[str] = Field(None, description="ID único del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: str = Field(..., description="Nombre completo del usuario")
    apellido: str = Field(..., description="Apellido del usuario")
    telefono: Optional[str] = Field(None, description="Teléfono del usuario")
    password_hash: Optional[str] = Field(None, description="Hash de la contraseña")
    fecha_registro: datetime = Field(default_factory=datetime.now, description="Fecha de registro")
    activo: bool = Field(default=True, description="Estado activo del usuario")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UsuarioCreate(BaseModel):
    """DTO para crear un usuario"""
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: str = Field(..., description="Nombre completo del usuario")
    apellido: str = Field(..., description="Apellido del usuario")
    telefono: Optional[str] = Field(None, description="Teléfono del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class UsuarioLogin(BaseModel):
    """DTO para login de usuario"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class UsuarioResponse(BaseModel):
    """DTO para respuesta de usuario (sin password)"""
    id: str = Field(..., description="ID único del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: str = Field(..., description="Nombre completo del usuario")
    apellido: str = Field(..., description="Apellido del usuario")
    telefono: Optional[str] = Field(None, description="Teléfono del usuario")
    fecha_registro: datetime = Field(..., description="Fecha de registro")
    activo: bool = Field(..., description="Estado activo del usuario")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenResponse(BaseModel):
    """DTO para respuesta con token JWT"""
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en minutos")


class LoginResponse(BaseModel):
    """DTO para respuesta de login con token"""
    usuario: UsuarioResponse = Field(..., description="Información del usuario")
    token: TokenResponse = Field(..., description="Token de autenticación")
    mensaje: str = Field(..., description="Mensaje de confirmación")


class RegistroResponse(BaseModel):
    """DTO para respuesta de registro con token"""
    usuario: UsuarioResponse = Field(..., description="Información del usuario")
    token: TokenResponse = Field(..., description="Token de autenticación")
    mensaje: str = Field(..., description="Mensaje de confirmación") 