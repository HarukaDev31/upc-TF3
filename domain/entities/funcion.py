from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class TipoSala(str, Enum):
    ESTANDAR = "estandar"
    VIP = "vip"
    IMAX = "imax"
    DBOX = "4dx"
    DOLBY_ATMOS = "dolby_atmos"


class EstadoFuncion(str, Enum):
    PROGRAMADA = "programada"
    EN_CURSO = "en_curso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class Asiento(BaseModel):
    fila: str = Field(..., min_length=1, max_length=2)
    numero: int = Field(..., gt=0, le=50)
    tipo: str = Field(default="estandar")  # estandar, vip, discapacitado
    precio_adicional: float = Field(default=0.0, ge=0)
    
    @property
    def codigo(self) -> str:
        """Retorna el código del asiento como A5, B10, etc."""
        return f"{self.fila}{self.numero}"
    
    def to_bit_position(self, asientos_por_fila: int = 20) -> int:
        """Convierte el asiento a posición de bit para Redis bitmap"""
        fila_num = ord(self.fila.upper()) - ord('A')
        return (fila_num * asientos_por_fila) + self.numero


class Sala(BaseModel):
    id: str
    nombre: str
    tipo: TipoSala
    capacidad_total: int = Field(..., gt=0)
    filas: int = Field(..., gt=0)
    asientos_por_fila: int = Field(..., gt=0)
    asientos: List[Asiento] = Field(default_factory=list)
    equipamiento: List[str] = Field(default_factory=list)
    
    def generar_mapa_asientos(self) -> Dict[str, List[Asiento]]:
        """Genera el mapa de asientos organizados por fila"""
        mapa = {}
        for asiento in self.asientos:
            if asiento.fila not in mapa:
                mapa[asiento.fila] = []
            mapa[asiento.fila].append(asiento)
        return mapa


class Funcion(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    pelicula_id: str = Field(..., min_length=1)
    sala: Sala
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    precio_base: float = Field(..., gt=0)
    precio_vip: Optional[float] = Field(None, gt=0)
    estado: EstadoFuncion = EstadoFuncion.PROGRAMADA
    subtitulos: bool = Field(default=False)
    idioma_audio: str = Field(..., min_length=2)
    
    # Control de ocupación
    asientos_ocupados: List[str] = Field(default_factory=list)
    asientos_reservados: List[str] = Field(default_factory=list)
    ventas_totales: int = Field(default=0, ge=0)
    ingresos_totales: float = Field(default=0.0, ge=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def asientos_disponibles(self) -> List[str]:
        """Retorna lista de asientos disponibles"""
        todos_asientos = [asiento.codigo for asiento in self.sala.asientos]
        ocupados_y_reservados = set(self.asientos_ocupados + self.asientos_reservados)
        return [asiento for asiento in todos_asientos if asiento not in ocupados_y_reservados]
    
    def capacidad_disponible(self) -> int:
        """Retorna el número de asientos disponibles"""
        return len(self.asientos_disponibles())
    
    def porcentaje_ocupacion(self) -> float:
        """Calcula el porcentaje de ocupación de la función"""
        if self.sala.capacidad_total == 0:
            return 0.0
        ocupados = len(self.asientos_ocupados)
        return (ocupados / self.sala.capacidad_total) * 100
    
    def puede_iniciar(self) -> bool:
        """Verifica si la función puede iniciar"""
        ahora = datetime.now()
        return (
            self.estado == EstadoFuncion.PROGRAMADA and
            ahora >= self.fecha_hora_inicio
        )
    
    def esta_en_horario_venta(self) -> bool:
        """Verifica si está en horario de venta (hasta 30 min después del inicio)"""
        ahora = datetime.now()
        limite_venta = self.fecha_hora_inicio.replace(minute=self.fecha_hora_inicio.minute + 30)
        return ahora <= limite_venta
    
    def calcular_precio_asiento(self, codigo_asiento: str) -> float:
        """Calcula el precio de un asiento específico"""
        asiento = next((a for a in self.sala.asientos if a.codigo == codigo_asiento), None)
        if not asiento:
            raise ValueError(f"Asiento {codigo_asiento} no encontrado")
        
        precio_base = self.precio_vip if asiento.tipo == "vip" else self.precio_base
        return precio_base + asiento.precio_adicional
    
    def reservar_asientos(self, asientos: List[str]) -> bool:
        """Reserva temporalmente una lista de asientos"""
        asientos_disp = self.asientos_disponibles()
        
        # Verificar que todos los asientos estén disponibles
        for asiento in asientos:
            if asiento not in asientos_disp:
                return False
        
        # Reservar asientos
        self.asientos_reservados.extend(asientos)
        return True
    
    def confirmar_venta(self, asientos: List[str]) -> None:
        """Confirma la venta moviendo asientos de reservados a ocupados"""
        for asiento in asientos:
            if asiento in self.asientos_reservados:
                self.asientos_reservados.remove(asiento)
                self.asientos_ocupados.append(asiento)
        
        self.ventas_totales += len(asientos)
        self.updated_at = datetime.now()
    
    def liberar_reserva(self, asientos: List[str]) -> None:
        """Libera asientos reservados"""
        for asiento in asientos:
            if asiento in self.asientos_reservados:
                self.asientos_reservados.remove(asiento)
        
        self.updated_at = datetime.now() 