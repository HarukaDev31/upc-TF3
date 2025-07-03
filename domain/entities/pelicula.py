from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class GeneroEnum(str, Enum):
    ACCION = "accion"
    AVENTURA = "aventura"
    COMEDIA = "comedia"
    DRAMA = "drama"
    TERROR = "terror"
    CIENCIA_FICCION = "ciencia_ficcion"
    ROMANCE = "romance"
    THRILLER = "thriller"
    ANIMACION = "animacion"
    DOCUMENTAL = "documental"


class ClasificacionEnum(str, Enum):
    G = "G"  # General
    PG = "PG"  # Parental Guidance
    PG13 = "PG-13"  # Parents Strongly Cautioned
    R = "R"  # Restricted
    NC17 = "NC-17"  # Adults Only


class Pelicula(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    titulo: str = Field(..., min_length=1, max_length=200)
    titulo_original: Optional[str] = Field(None, max_length=200)
    sinopsis: str = Field(..., min_length=10, max_length=2000)
    director: str = Field(..., min_length=2, max_length=100)
    actores_principales: List[str] = Field(default_factory=list)
    generos: List[GeneroEnum] = Field(..., min_items=1)
    duracion_minutos: int = Field(..., gt=0, le=600)
    clasificacion: ClasificacionEnum
    idioma_original: str = Field(..., min_length=2, max_length=50)
    subtitulos: List[str] = Field(default_factory=list)
    fecha_estreno: date
    fecha_disponible_desde: date
    fecha_disponible_hasta: Optional[date] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    precio_base: float = Field(..., gt=0)
    activa: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat()
        }
    
    def esta_disponible(self, fecha_consulta: date = None) -> bool:
        """Verifica si la película está disponible en una fecha dada"""
        if fecha_consulta is None:
            fecha_consulta = date.today()
        
        if not self.activa:
            return False
        
        if fecha_consulta < self.fecha_disponible_desde:
            return False
        
        if self.fecha_disponible_hasta and fecha_consulta > self.fecha_disponible_hasta:
            return False
        
        return True
    
    def calcular_precio_con_descuento(self, descuento_porcentaje: float) -> float:
        """Calcula el precio con descuento aplicado"""
        return self.precio_base * (1 - descuento_porcentaje)
    
    def es_apta_para_edad(self, edad: int) -> bool:
        """Verifica si la película es apta para una edad específica"""
        restricciones = {
            ClasificacionEnum.G: 0,
            ClasificacionEnum.PG: 0,  # Recomendación parental
            ClasificacionEnum.PG13: 13,
            ClasificacionEnum.R: 17,
            ClasificacionEnum.NC17: 18
        }
        return edad >= restricciones.get(self.clasificacion, 18) 