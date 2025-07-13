"""
Entidad SeleccionAsiento para el sistema de cine
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SeleccionAsiento(BaseModel):
    """Entidad SeleccionAsiento"""
    id: Optional[str] = Field(None, description="ID único de la selección")
    funcion_id: str = Field(..., description="ID de la función")
    usuario_id: str = Field(..., description="ID del usuario que seleccionó")
    asiento_id: str = Field(..., description="ID del asiento seleccionado")
    estado: str = Field(default="temporal", description="Estado: temporal, confirmada, cancelada")
    fecha_seleccion: datetime = Field(default_factory=datetime.now, description="Fecha de selección")
    fecha_expiracion: Optional[datetime] = Field(None, description="Fecha de expiración")
    fecha_confirmacion: Optional[datetime] = Field(None, description="Fecha de confirmación")
    fecha_cancelacion: Optional[datetime] = Field(None, description="Fecha de cancelación")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SeleccionAsientoCreate(BaseModel):
    """DTO para crear una selección"""
    funcion_id: str = Field(..., description="ID de la función")
    usuario_id: str = Field(..., description="ID del usuario")
    asiento_id: str = Field(..., description="ID del asiento")
    estado: str = Field(default="temporal", description="Estado inicial")


class SeleccionAsientoUpdate(BaseModel):
    """DTO para actualizar una selección"""
    estado: str = Field(..., description="Nuevo estado")
    fecha_confirmacion: Optional[datetime] = Field(None, description="Fecha de confirmación")
    fecha_cancelacion: Optional[datetime] = Field(None, description="Fecha de cancelación")


class SeleccionAsientoResponse(BaseModel):
    """DTO para respuesta de selección"""
    id: str = Field(..., description="ID único de la selección")
    funcion_id: str = Field(..., description="ID de la función")
    usuario_id: str = Field(..., description="ID del usuario")
    asiento_id: str = Field(..., description="ID del asiento")
    estado: str = Field(..., description="Estado de la selección")
    fecha_seleccion: datetime = Field(..., description="Fecha de selección")
    fecha_expiracion: Optional[datetime] = Field(None, description="Fecha de expiración")
    fecha_confirmacion: Optional[datetime] = Field(None, description="Fecha de confirmación")
    fecha_cancelacion: Optional[datetime] = Field(None, description="Fecha de cancelación")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HistorialSeleccion(BaseModel):
    """DTO para historial de selecciones por función"""
    funcion_id: str = Field(..., description="ID de la función")
    selecciones: list[SeleccionAsientoResponse] = Field(..., description="Lista de selecciones")
    total_selecciones: int = Field(..., description="Total de selecciones")
    selecciones_temporales: int = Field(..., description="Selecciones temporales")
    selecciones_confirmadas: int = Field(..., description="Selecciones confirmadas")
    selecciones_canceladas: int = Field(..., description="Selecciones canceladas") 