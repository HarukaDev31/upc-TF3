from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TipoCliente(str, Enum):
    REGULAR = "regular"
    FRECUENTE = "frecuente"
    PREMIUM = "premium"


class Cliente(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nombre: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    telefono: Optional[str] = Field(None, min_length=8, max_length=15)
    tipo: TipoCliente = TipoCliente.REGULAR
    fecha_registro: datetime = Field(default_factory=datetime.now)
    historial_compras: List[str] = Field(default_factory=list)
    puntos_acumulados: int = Field(default=0, ge=0)
    activo: bool = Field(default=True)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def calcular_descuento(self) -> float:
        """Calcula el descuento basado en el tipo de cliente"""
        descuentos = {
            TipoCliente.REGULAR: 0.0,
            TipoCliente.FRECUENTE: 0.10,
            TipoCliente.PREMIUM: 0.20
        }
        return descuentos.get(self.tipo, 0.0)
    
    def agregar_puntos(self, monto: float) -> None:
        """Agrega puntos basado en el monto de la compra"""
        puntos_por_peso = 1
        self.puntos_acumulados += int(monto * puntos_por_peso)
    
    def puede_usar_descuento_puntos(self, puntos_requeridos: int) -> bool:
        """Verifica si el cliente tiene suficientes puntos para un descuento"""
        return self.puntos_acumulados >= puntos_requeridos 