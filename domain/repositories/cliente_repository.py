from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.cliente import Cliente


class ClienteRepository(ABC):
    """Interfaz del repositorio de clientes - Puerto en Clean Architecture"""
    
    @abstractmethod
    async def crear(self, cliente: Cliente) -> Cliente:
        """Crea un nuevo cliente"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, cliente_id: str) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        pass
    
    @abstractmethod
    async def obtener_por_email(self, email: str) -> Optional[Cliente]:
        """Obtiene un cliente por su email"""
        pass
    
    @abstractmethod
    async def actualizar(self, cliente: Cliente) -> Cliente:
        """Actualiza un cliente existente"""
        pass
    
    @abstractmethod
    async def eliminar(self, cliente_id: str) -> bool:
        """Elimina un cliente (soft delete)"""
        pass
    
    @abstractmethod
    async def listar(self, limite: int = 50, offset: int = 0) -> List[Cliente]:
        """Lista clientes con paginación"""
        pass
    
    @abstractmethod
    async def buscar_por_nombre(self, nombre: str) -> List[Cliente]:
        """Busca clientes por nombre"""
        pass
    
    @abstractmethod
    async def obtener_historial_compras(self, cliente_id: str) -> List[str]:
        """Obtiene el historial de compras de un cliente"""
        pass
    
    @abstractmethod
    async def actualizar_puntos(self, cliente_id: str, puntos: int) -> bool:
        """Actualiza los puntos acumulados de un cliente"""
        pass 