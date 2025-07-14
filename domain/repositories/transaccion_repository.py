"""
Repositorio de Transacciones para MongoDB
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from domain.entities.transaccion import Transaccion, EstadoTransaccion, MetodoPago, DetalleAsiento, DetallePago


class TransaccionRepository:
    """Repositorio para operaciones de transacciones"""
    
    def __init__(self, database):
        self.database = database
        self.collection = database.transacciones
    
    async def crear_transaccion(self, transaccion: Transaccion) -> Optional[Transaccion]:
        """Crear una nueva transacción"""
        try:
            # Convertir a diccionario para MongoDB
            transaccion_dict = transaccion.dict(by_alias=True)
            
            # Insertar en MongoDB
            result = await self.collection.insert_one(transaccion_dict)
            
            # Actualizar ID
            if result.inserted_id:
                transaccion.id = str(result.inserted_id)
            
            return transaccion
            
        except Exception as e:
            print(f"Error creando transacción: {e}")
            return None
    
    async def obtener_transaccion_por_id(self, transaccion_id: str) -> Optional[Transaccion]:
        """Obtener transacción por ID"""
        try:
            transaccion_doc = await self.collection.find_one({"_id": ObjectId(transaccion_id)})
            if not transaccion_doc:
                return None
            
            # Convertir de MongoDB a objeto Transaccion
            return Transaccion(**transaccion_doc)
            
        except Exception as e:
            print(f"Error obteniendo transacción: {e}")
            return None
    
    async def obtener_transacciones_por_cliente(self, cliente_id: str, limit: int = 50) -> List[Transaccion]:
        """Obtener transacciones de un cliente"""
        try:
            transacciones = []
            cursor = self.collection.find({"cliente_id": cliente_id}).sort("fecha_creacion", -1).limit(limit)
            
            async for transaccion_doc in cursor:
                transacciones.append(Transaccion(**transaccion_doc))
            
            return transacciones
            
        except Exception as e:
            print(f"Error obteniendo transacciones del cliente: {e}")
            return []
    
    async def obtener_transacciones_por_funcion(self, funcion_id: str) -> List[Transaccion]:
        """Obtener transacciones de una función"""
        try:
            transacciones = []
            cursor = self.collection.find({"funcion_id": funcion_id})
            
            async for transaccion_doc in cursor:
                transacciones.append(Transaccion(**transaccion_doc))
            
            return transacciones
            
        except Exception as e:
            print(f"Error obteniendo transacciones de la función: {e}")
            return []
    
    async def actualizar_estado_transaccion(self, transaccion_id: str, nuevo_estado: EstadoTransaccion, observacion: str = None) -> bool:
        """Actualizar el estado de una transacción"""
        try:
            update_data = {
                "estado": nuevo_estado,
                "fecha_actualizacion": datetime.now()
            }
            
            if nuevo_estado == EstadoTransaccion.CONFIRMADO:
                update_data["fecha_confirmacion"] = datetime.now()
            
            if observacion:
                update_data["observaciones"] = observacion
            
            # Intentar con ObjectId primero, si falla usar el ID como string
            try:
                result = await self.collection.update_one(
                    {"_id": ObjectId(transaccion_id)},
                    {"$set": update_data}
                )
            except:
                # Si no es un ObjectId válido, buscar por el ID como string
                result = await self.collection.update_one(
                    {"_id": transaccion_id},
                    {"$set": update_data}
                )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error actualizando estado de transacción: {e}")
            return False
    
    async def obtener_transacciones_pendientes(self) -> List[Transaccion]:
        """Obtener transacciones pendientes"""
        try:
            transacciones = []
            cursor = self.collection.find({"estado": EstadoTransaccion.PENDIENTE})
            
            async for transaccion_doc in cursor:
                transacciones.append(Transaccion(**transaccion_doc))
            
            return transacciones
            
        except Exception as e:
            print(f"Error obteniendo transacciones pendientes: {e}")
            return []
    
    async def obtener_transacciones_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Transaccion]:
        """Obtener transacciones en un rango de fechas"""
        try:
            transacciones = []
            cursor = self.collection.find({
                "fecha_creacion": {
                    "$gte": fecha_inicio,
                    "$lte": fecha_fin
                }
            }).sort("fecha_creacion", -1)
            
            async for transaccion_doc in cursor:
                transacciones.append(Transaccion(**transaccion_doc))
            
            return transacciones
            
        except Exception as e:
            print(f"Error obteniendo transacciones por fecha: {e}")
            return []
    
    async def obtener_estadisticas_ventas(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Obtener estadísticas de ventas"""
        try:
            pipeline = [
                {
                    "$match": {
                        "fecha_creacion": {
                            "$gte": fecha_inicio,
                            "$lte": fecha_fin
                        },
                        "estado": EstadoTransaccion.CONFIRMADO
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_ventas": {"$sum": "$total"},
                        "cantidad_transacciones": {"$sum": 1},
                        "cantidad_asientos": {"$sum": "$cantidad_asientos"},
                        "promedio_por_transaccion": {"$avg": "$total"}
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                return result[0]
            else:
                return {
                    "total_ventas": 0,
                    "cantidad_transacciones": 0,
                    "cantidad_asientos": 0,
                    "promedio_por_transaccion": 0
                }
                
        except Exception as e:
            print(f"Error obteniendo estadísticas de ventas: {e}")
            return {
                "total_ventas": 0,
                "cantidad_transacciones": 0,
                "cantidad_asientos": 0,
                "promedio_por_transaccion": 0
            }
    
    async def verificar_asientos_disponibles(self, funcion_id: str, asientos: List[str]) -> bool:
        """Verificar si los asientos están disponibles para compra"""
        try:
            # Buscar transacciones confirmadas que incluyan estos asientos
            pipeline = [
                {
                    "$match": {
                        "funcion_id": funcion_id,
                        "estado": EstadoTransaccion.CONFIRMADO
                    }
                },
                {
                    "$unwind": "$asientos"
                },
                {
                    "$match": {
                        "asientos.codigo": {"$in": asientos}
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            
            # Si hay resultados, significa que los asientos están ocupados
            return len(result) == 0
            
        except Exception as e:
            print(f"Error verificando disponibilidad de asientos: {e}")
            return False
    
    async def obtener_asientos_ocupados_funcion(self, funcion_id: str) -> List[str]:
        """Obtener lista de asientos ocupados en una función"""
        try:
            pipeline = [
                {
                    "$match": {
                        "funcion_id": funcion_id,
                        "estado": EstadoTransaccion.CONFIRMADO
                    }
                },
                {
                    "$unwind": "$asientos"
                },
                {
                    "$group": {
                        "_id": "$asientos.codigo"
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            
            return [doc["_id"] for doc in result]
            
        except Exception as e:
            print(f"Error obteniendo asientos ocupados: {e}")
            return [] 