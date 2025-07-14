"""
Repositorio de SeleccionAsiento para MongoDB
"""

from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId

from domain.entities.seleccion_asiento import (
    SeleccionAsiento, 
    SeleccionAsientoCreate, 
    SeleccionAsientoUpdate,
    SeleccionAsientoResponse,
    HistorialSeleccion
)


class SeleccionAsientoRepository:
    """Repositorio para operaciones de selecciones de asientos"""
    
    def __init__(self, database):
        self.database = database
        self.collection = database.selecciones_asientos
    
    async def crear_seleccion(self, seleccion_data: SeleccionAsientoCreate) -> Optional[SeleccionAsientoResponse]:
        """Crear una nueva selección de asiento"""
        try:
            # Verificar si el asiento ya está seleccionado por otro usuario
            existing_selection = await self.collection.find_one({
                "funcion_id": seleccion_data.funcion_id,
                "asiento_id": seleccion_data.asiento_id,
                "estado": {"$in": ["temporal", "confirmada"]}
            })
            
            if existing_selection:
                return None
            
            # Crear documento de selección
            seleccion_doc = {
                "funcion_id": seleccion_data.funcion_id,
                "usuario_id": seleccion_data.usuario_id,
                "asiento_id": seleccion_data.asiento_id,
                "estado": seleccion_data.estado,
                "fecha_seleccion": datetime.now(),
                "fecha_expiracion": datetime.now() + timedelta(minutes=5) if seleccion_data.estado == "temporal" else None
            }
            
            # Insertar en MongoDB
            result = await self.collection.insert_one(seleccion_doc)
            
            # Crear respuesta
            seleccion_response = SeleccionAsientoResponse(
                id=str(result.inserted_id),
                funcion_id=seleccion_data.funcion_id,
                usuario_id=seleccion_data.usuario_id,
                asiento_id=seleccion_data.asiento_id,
                estado=seleccion_data.estado,
                fecha_seleccion=seleccion_doc["fecha_seleccion"],
                fecha_expiracion=seleccion_doc["fecha_expiracion"],
                fecha_confirmacion=None,
                fecha_cancelacion=None
            )
            
            return seleccion_response
            
        except Exception as e:
            print(f"Error creando selección: {e}")
            return None
    
    async def obtener_seleccion_por_id(self, seleccion_id: str) -> Optional[SeleccionAsientoResponse]:
        """Obtener selección por ID"""
        try:
            seleccion_doc = await self.collection.find_one({"_id": ObjectId(seleccion_id)})
            if not seleccion_doc:
                return None
            
            return SeleccionAsientoResponse(
                id=str(seleccion_doc["_id"]),
                funcion_id=seleccion_doc["funcion_id"],
                usuario_id=seleccion_doc["usuario_id"],
                asiento_id=seleccion_doc["asiento_id"],
                estado=seleccion_doc["estado"],
                fecha_seleccion=seleccion_doc["fecha_seleccion"],
                fecha_expiracion=seleccion_doc.get("fecha_expiracion"),
                fecha_confirmacion=seleccion_doc.get("fecha_confirmacion"),
                fecha_cancelacion=seleccion_doc.get("fecha_cancelacion")
            )
            
        except Exception as e:
            print(f"Error obteniendo selección: {e}")
            return None
    
    async def obtener_selecciones_por_funcion(self, funcion_id: str) -> List[SeleccionAsientoResponse]:
        """Obtener todas las selecciones de una función"""
        try:
            selecciones = []
            cursor = self.collection.find({"funcion_id": funcion_id})
            
            async for seleccion_doc in cursor:
                selecciones.append(SeleccionAsientoResponse(
                    id=str(seleccion_doc["_id"]),
                    funcion_id=seleccion_doc["funcion_id"],
                    usuario_id=seleccion_doc["usuario_id"],
                    asiento_id=seleccion_doc["asiento_id"],
                    estado=seleccion_doc["estado"],
                    fecha_seleccion=seleccion_doc["fecha_seleccion"],
                    fecha_expiracion=seleccion_doc.get("fecha_expiracion"),
                    fecha_confirmacion=seleccion_doc.get("fecha_confirmacion"),
                    fecha_cancelacion=seleccion_doc.get("fecha_cancelacion")
                ))
            
            return selecciones
            
        except Exception as e:
            print(f"Error obteniendo selecciones por función: {e}")
            return []
    
    async def obtener_selecciones_por_usuario(self, usuario_id: str) -> List[SeleccionAsientoResponse]:
        """Obtener todas las selecciones de un usuario"""
        try:
            selecciones = []
            cursor = self.collection.find({"usuario_id": usuario_id})
            
            async for seleccion_doc in cursor:
                selecciones.append(SeleccionAsientoResponse(
                    id=str(seleccion_doc["_id"]),
                    funcion_id=seleccion_doc["funcion_id"],
                    usuario_id=seleccion_doc["usuario_id"],
                    asiento_id=seleccion_doc["asiento_id"],
                    estado=seleccion_doc["estado"],
                    fecha_seleccion=seleccion_doc["fecha_seleccion"],
                    fecha_expiracion=seleccion_doc.get("fecha_expiracion"),
                    fecha_confirmacion=seleccion_doc.get("fecha_confirmacion"),
                    fecha_cancelacion=seleccion_doc.get("fecha_cancelacion")
                ))
            
            return selecciones
            
        except Exception as e:
            print(f"Error obteniendo selecciones por usuario: {e}")
            return []
    
    async def actualizar_seleccion(self, seleccion_id: str, datos_actualizacion: SeleccionAsientoUpdate) -> Optional[SeleccionAsientoResponse]:
        """Actualizar estado de una selección"""
        try:
            update_data = {"estado": datos_actualizacion.estado}
            
            if datos_actualizacion.fecha_confirmacion:
                update_data["fecha_confirmacion"] = datos_actualizacion.fecha_confirmacion
            
            if datos_actualizacion.fecha_cancelacion:
                update_data["fecha_cancelacion"] = datos_actualizacion.fecha_cancelacion
            
            result = await self.collection.update_one(
                {"_id": ObjectId(seleccion_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.obtener_seleccion_por_id(seleccion_id)
            
            return None
            
        except Exception as e:
            print(f"Error actualizando selección: {e}")
            return None
    
    async def cancelar_seleccion(self, seleccion_id: str) -> bool:
        """Cancelar una selección"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(seleccion_id)},
                {
                    "$set": {
                        "estado": "cancelada",
                        "fecha_cancelacion": datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error cancelando selección: {e}")
            return False
    
    async def confirmar_seleccion(self, seleccion_id: str) -> bool:
        """Confirmar una selección"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(seleccion_id)},
                {
                    "$set": {
                        "estado": "confirmada",
                        "fecha_confirmacion": datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error confirmando selección: {e}")
            return False
    
    async def actualizar_estado_seleccion(self, usuario_id: str, funcion_id: str, asiento_id: str, nuevo_estado: str, fecha_actualizacion: datetime) -> bool:
        """Actualizar estado de una selección específica"""
        try:
            update_data = {
                "estado": nuevo_estado
            }
            
            if nuevo_estado == "confirmada":
                update_data["fecha_confirmacion"] = fecha_actualizacion
            elif nuevo_estado == "cancelada":
                update_data["fecha_cancelacion"] = fecha_actualizacion
            
            result = await self.collection.update_one(
                {
                    "usuario_id": usuario_id,
                    "funcion_id": funcion_id,
                    "asiento_id": asiento_id,
                    "estado": "temporal"  # Solo actualizar selecciones temporales
                },
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error actualizando estado de selección: {e}")
            return False
    
    async def limpiar_selecciones_expiradas(self) -> int:
        """Limpiar selecciones temporales expiradas"""
        try:
            result = await self.collection.update_many(
                {
                    "estado": "temporal",
                    "fecha_expiracion": {"$lt": datetime.now()}
                },
                {
                    "$set": {
                        "estado": "expirada",
                        "fecha_cancelacion": datetime.now()
                    }
                }
            )
            
            return result.modified_count
            
        except Exception as e:
            print(f"Error limpiando selecciones expiradas: {e}")
            return 0
    
    async def obtener_historial_funcion(self, funcion_id: str) -> HistorialSeleccion:
        """Obtener historial completo de selecciones de una función"""
        try:
            selecciones = await self.obtener_selecciones_por_funcion(funcion_id)
            
            # Contar por estado
            temporales = len([s for s in selecciones if s.estado == "temporal"])
            confirmadas = len([s for s in selecciones if s.estado == "confirmada"])
            canceladas = len([s for s in selecciones if s.estado in ["cancelada", "expirada"]])
            
            return HistorialSeleccion(
                funcion_id=funcion_id,
                selecciones=selecciones,
                total_selecciones=len(selecciones),
                selecciones_temporales=temporales,
                selecciones_confirmadas=confirmadas,
                selecciones_canceladas=canceladas
            )
            
        except Exception as e:
            print(f"Error obteniendo historial de función: {e}")
            return HistorialSeleccion(
                funcion_id=funcion_id,
                selecciones=[],
                total_selecciones=0,
                selecciones_temporales=0,
                selecciones_confirmadas=0,
                selecciones_canceladas=0
            ) 