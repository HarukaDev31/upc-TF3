import motor.motor_asyncio
from typing import Optional, List, Dict, Any
from pymongo import IndexModel
from config.settings import settings


class MongoDBService:
    """
    Servicio de MongoDB para persistencia de datos del sistema de cine
    """
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database = None
        
    async def connect(self):
        """Establece conexión con MongoDB"""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=settings.mongodb_max_connections
        )
        
        self.database = self.client[settings.mongodb_database]
        
        # Verificar conexión
        await self.client.admin.command('ping')
        
        # Crear índices
        await self._create_indexes()
        
    async def disconnect(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
    
    async def _create_indexes(self):
        """Crea índices optimizados para las consultas del sistema"""
        
        # Índices para clientes
        await self.database.clientes.create_indexes([
            IndexModel([("email", 1)], unique=True),
            IndexModel([("tipo", 1)]),
            IndexModel([("activo", 1)]),
            IndexModel([("fecha_registro", -1)])
        ])
        
        # Índices para películas
        await self.database.peliculas.create_indexes([
            IndexModel([("titulo", "text"), ("sinopsis", "text")]),
            IndexModel([("generos", 1)]),
            IndexModel([("fecha_estreno", -1)]),
            IndexModel([("activa", 1)]),
            IndexModel([("director", 1)])
        ])
        
        # Índices para funciones
        await self.database.funciones.create_indexes([
            IndexModel([("pelicula_id", 1)]),
            IndexModel([("sala.id", 1)]),
            IndexModel([("fecha_hora_inicio", 1)]),
            IndexModel([("estado", 1)]),
            IndexModel([("pelicula_id", 1), ("fecha_hora_inicio", 1)])
        ])
        
        # Índices para transacciones
        await self.database.transacciones.create_indexes([
            IndexModel([("cliente_id", 1)]),
            IndexModel([("funcion_id", 1)]),
            IndexModel([("estado", 1)]),
            IndexModel([("fecha_creacion", -1)]),
            IndexModel([("numero_factura", 1)], unique=True),
            IndexModel([("cliente_id", 1), ("fecha_creacion", -1)])
        ])
    
    # Operaciones para clientes
    async def crear_cliente(self, cliente_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo cliente"""
        result = await self.database.clientes.insert_one(cliente_data)
        cliente_data["_id"] = str(result.inserted_id)
        return cliente_data
    
    async def obtener_cliente(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por ID"""
        return await self.database.clientes.find_one({"_id": cliente_id})
    
    async def obtener_cliente_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por email"""
        return await self.database.clientes.find_one({"email": email})
    
    async def actualizar_cliente(self, cliente_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualiza un cliente"""
        result = await self.database.clientes.update_one(
            {"_id": cliente_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # Operaciones para películas
    async def crear_pelicula(self, pelicula_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva película"""
        result = await self.database.peliculas.insert_one(pelicula_data)
        pelicula_data["_id"] = str(result.inserted_id)
        return pelicula_data
    
    async def obtener_pelicula(self, pelicula_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una película por ID"""
        return await self.database.peliculas.find_one({"_id": pelicula_id})
    
    async def buscar_peliculas(self, filtros: Dict[str, Any], limite: int = 50) -> List[Dict[str, Any]]:
        """Busca películas con filtros"""
        cursor = self.database.peliculas.find(filtros).limit(limite)
        return await cursor.to_list(length=limite)
    
    async def buscar_peliculas_texto(self, texto: str, limite: int = 50) -> List[Dict[str, Any]]:
        """Búsqueda de texto completo en películas"""
        filtros = {
            "$text": {"$search": texto},
            "activa": True
        }
        cursor = self.database.peliculas.find(
            filtros,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limite)
        
        return await cursor.to_list(length=limite)
    
    # Operaciones para funciones
    async def crear_funcion(self, funcion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva función"""
        result = await self.database.funciones.insert_one(funcion_data)
        funcion_data["_id"] = str(result.inserted_id)
        return funcion_data
    
    async def obtener_funcion(self, funcion_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una función por ID"""
        return await self.database.funciones.find_one({"_id": funcion_id})
    
    async def listar_funciones_pelicula(self, pelicula_id: str) -> List[Dict[str, Any]]:
        """Lista funciones de una película"""
        cursor = self.database.funciones.find(
            {"pelicula_id": pelicula_id, "estado": {"$ne": "cancelada"}}
        ).sort("fecha_hora_inicio", 1)
        
        return await cursor.to_list(length=100)
    
    async def actualizar_funcion(self, funcion_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualiza una función"""
        result = await self.database.funciones.update_one(
            {"_id": funcion_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # Operaciones para transacciones
    async def guardar_transaccion(self, transaccion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda una transacción"""
        result = await self.database.transacciones.insert_one(transaccion_data)
        transaccion_data["_id"] = str(result.inserted_id)
        return transaccion_data
    
    async def obtener_transaccion(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una transacción por ID"""
        return await self.database.transacciones.find_one({"_id": transaccion_id})
    
    async def actualizar_transaccion(self, transaccion_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualiza una transacción"""
        result = await self.database.transacciones.update_one(
            {"_id": transaccion_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def listar_transacciones_cliente(self, cliente_id: str, limite: int = 20) -> List[Dict[str, Any]]:
        """Lista transacciones de un cliente"""
        cursor = self.database.transacciones.find(
            {"cliente_id": cliente_id}
        ).sort("fecha_creacion", -1).limit(limite)
        
        return await cursor.to_list(length=limite)
    
    # Reportes y métricas
    async def obtener_metricas_ventas(self, fecha_inicio: str, fecha_fin: str) -> Dict[str, Any]:
        """Obtiene métricas de ventas en un período"""
        pipeline = [
            {
                "$match": {
                    "estado": "confirmado",
                    "fecha_creacion": {
                        "$gte": fecha_inicio,
                        "$lte": fecha_fin
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_ventas": {"$sum": "$total"},
                    "total_transacciones": {"$sum": 1},
                    "promedio_venta": {"$avg": "$total"},
                    "total_asientos": {"$sum": "$cantidad_asientos"}
                }
            }
        ]
        
        result = await self.database.transacciones.aggregate(pipeline).to_list(1)
        return result[0] if result else {}
    
    async def obtener_peliculas_mas_vendidas(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtiene las películas más vendidas"""
        pipeline = [
            {
                "$match": {"estado": "confirmado"}
            },
            {
                "$group": {
                    "_id": "$pelicula_id",
                    "total_ventas": {"$sum": "$total"},
                    "total_asientos": {"$sum": "$cantidad_asientos"},
                    "total_transacciones": {"$sum": 1}
                }
            },
            {
                "$sort": {"total_asientos": -1}
            },
            {
                "$limit": limite
            },
            {
                "$lookup": {
                    "from": "peliculas",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "pelicula"
                }
            },
            {
                "$unwind": "$pelicula"
            }
        ]
        
        return await self.database.transacciones.aggregate(pipeline).to_list(limite)
    
    # Operaciones de limpieza y mantenimiento
    async def limpiar_reservas_vencidas(self):
        """Limpia reservas vencidas (complementa la limpieza de Redis)"""
        # Las reservas temporales están principalmente en Redis
        # Aquí podríamos limpiar transacciones pendientes muy antiguas
        result = await self.database.transacciones.delete_many({
            "estado": "pendiente",
            "fecha_creacion": {
                "$lt": "2024-01-01T00:00:00Z"  # Ejemplo de fecha límite
            }
        })
        return result.deleted_count
    
    # Métodos adicionales para controladores
    async def listar_transacciones_funcion(self, funcion_id: str) -> List[Dict[str, Any]]:
        """Lista transacciones de una función específica"""
        cursor = self.database.transacciones.find(
            {"funcion_id": funcion_id, "estado": "confirmado"}
        ).sort("fecha_creacion", -1)
        
        return await cursor.to_list(length=100)
    
    async def contar_peliculas_activas(self) -> int:
        """Cuenta películas activas"""
        return await self.database.peliculas.count_documents({"activa": True})
    
    async def contar_funciones_hoy(self) -> int:
        """Cuenta funciones programadas para hoy"""
        from datetime import datetime, date
        hoy = date.today().isoformat()
        
        return await self.database.funciones.count_documents({
            "fecha_hora_inicio": {
                "$gte": f"{hoy}T00:00:00Z",
                "$lt": f"{hoy}T23:59:59Z"
            }
        })
    
    async def contar_transacciones_hoy(self) -> int:
        """Cuenta transacciones realizadas hoy"""
        from datetime import datetime, date
        hoy = date.today().isoformat()
        
        return await self.database.transacciones.count_documents({
            "fecha_creacion": {
                "$gte": f"{hoy}T00:00:00Z",
                "$lt": f"{hoy}T23:59:59Z"
            },
            "estado": "confirmado"
        }) 