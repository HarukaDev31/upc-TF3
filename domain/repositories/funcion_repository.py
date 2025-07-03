from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime, date
from domain.entities.funcion import Funcion


class FuncionRepository(ABC):
    """Interfaz del repositorio de funciones - Puerto en Clean Architecture"""
    
    @abstractmethod
    async def crear(self, funcion: Funcion) -> Funcion:
        """Crea una nueva función"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, funcion_id: str) -> Optional[Funcion]:
        """Obtiene una función por su ID"""
        pass
    
    @abstractmethod
    async def actualizar(self, funcion: Funcion) -> Funcion:
        """Actualiza una función existente"""
        pass
    
    @abstractmethod
    async def eliminar(self, funcion_id: str) -> bool:
        """Elimina una función"""
        pass
    
    @abstractmethod
    async def listar_por_pelicula(self, pelicula_id: str) -> List[Funcion]:
        """Lista todas las funciones de una película"""
        pass
    
    @abstractmethod
    async def listar_por_fecha(self, fecha: date) -> List[Funcion]:
        """Lista funciones por fecha"""
        pass
    
    @abstractmethod
    async def listar_por_sala(self, sala_id: str, fecha_inicio: datetime, fecha_fin: datetime) -> List[Funcion]:
        """Lista funciones de una sala en un rango de fechas"""
        pass
    
    @abstractmethod
    async def obtener_asientos_disponibles(self, funcion_id: str) -> List[str]:
        """Obtiene los asientos disponibles de una función"""
        pass
    
    @abstractmethod
    async def reservar_asientos(self, funcion_id: str, asientos: List[str]) -> bool:
        """Reserva asientos temporalmente"""
        pass
    
    @abstractmethod
    async def confirmar_asientos(self, funcion_id: str, asientos: List[str]) -> bool:
        """Confirma la ocupación de asientos"""
        pass
    
    @abstractmethod
    async def liberar_asientos(self, funcion_id: str, asientos: List[str]) -> bool:
        """Libera asientos reservados"""
        pass
    
    @abstractmethod
    async def verificar_disponibilidad(self, funcion_id: str, asientos: List[str]) -> bool:
        """Verifica si los asientos están disponibles"""
        pass 