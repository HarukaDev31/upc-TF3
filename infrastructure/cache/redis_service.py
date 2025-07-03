import redis.asyncio as redis
import asyncio
import json
from typing import Optional, Dict, List, Any, Union
from config.settings import settings


class RedisService:
    """
    Servicio de Redis optimizado para el sistema de cine
    Implementa operaciones de cache, bitmaps, sorted sets y streams
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Establece conexión con Redis con configuración optimizada para WSL"""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True,
            max_connections=settings.redis_pool_max_connections,
            socket_timeout=settings.redis_socket_timeout,
            socket_connect_timeout=settings.redis_socket_connect_timeout,
            socket_keepalive=settings.redis_socket_keepalive,
            socket_keepalive_options=settings.redis_socket_keepalive_options,
            retry_on_timeout=True,
            retry_on_error=[redis.ConnectionError, redis.TimeoutError],
            health_check_interval=30
        )
        
        # Verificar conexión con retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.redis_client.ping()
                print(f"✅ Conectado a Redis en {settings.redis_host}:{settings.redis_port}")
                break
            except (redis.ConnectionError, redis.TimeoutError) as e:
                if attempt == max_retries - 1:
                    print(f"❌ Error conectando a Redis después de {max_retries} intentos")
                    print(f"   Host: {settings.redis_host}:{settings.redis_port}")
                    print(f"   Error: {e}")
                    if settings.redis_host != "localhost":
                        print("💡 Tip: Prueba cambiar REDIS_HOST=localhost en tu archivo .env")
                    raise
                else:
                    print(f"⚠️  Intento {attempt + 1} fallido, reintentando...")
                    await asyncio.sleep(1)
        
    async def disconnect(self):
        """Cierra la conexión con Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    # Operaciones básicas de cache
    async def get(self, key: str) -> Optional[str]:
        """Obtiene un valor por clave"""
        return await self.redis_client.get(key)
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Establece un valor con TTL opcional"""
        return await self.redis_client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """Elimina una clave"""
        return await self.redis_client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe"""
        return await self.redis_client.exists(key) > 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Establece TTL para una clave"""
        return await self.redis_client.expire(key, seconds)
    
    # Operaciones de Hash
    async def hset(self, key: str, mapping: Dict[str, Any]) -> int:
        """Establece múltiples campos en un hash"""
        return await self.redis_client.hset(key, mapping=mapping)
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Obtiene un campo de un hash"""
        return await self.redis_client.hget(key, field)
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Obtiene todos los campos de un hash"""
        return await self.redis_client.hgetall(key)
    
    async def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        """Incrementa un campo numérico en un hash"""
        return await self.redis_client.hincrby(key, field, amount)
    
    # Operaciones de Bitmap (para asientos)
    async def setbit(self, key: str, offset: int, value: int) -> int:
        """Establece un bit en una posición específica"""
        return await self.redis_client.setbit(key, offset, value)
    
    async def getbit(self, key: str, offset: int) -> int:
        """Obtiene el valor de un bit en una posición específica"""
        return await self.redis_client.getbit(key, offset)
    
    async def bitcount(self, key: str, start: Optional[int] = None, end: Optional[int] = None) -> int:
        """Cuenta los bits establecidos en 1"""
        if start is not None and end is not None:
            return await self.redis_client.bitcount(key, start, end)
        return await self.redis_client.bitcount(key)
    
    # Operaciones de Sorted Set (para rankings)
    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Agrega elementos a un sorted set"""
        return await self.redis_client.zadd(key, mapping)
    
    async def zincrby(self, key: str, amount: float, member: str) -> float:
        """Incrementa el score de un miembro en un sorted set"""
        return await self.redis_client.zincrby(key, amount, member)
    
    async def zrange(self, key: str, start: int, end: int, desc: bool = False, withscores: bool = False) -> List:
        """Obtiene un rango de elementos de un sorted set"""
        return await self.redis_client.zrange(key, start, end, desc=desc, withscores=withscores)
    
    async def zrevrank(self, key: str, member: str) -> Optional[int]:
        """Obtiene el ranking de un miembro (orden descendente)"""
        return await self.redis_client.zrevrank(key, member)
    
    # Operaciones de HyperLogLog (para conteo único)
    async def pfadd(self, key: str, *elements: str) -> int:
        """Agrega elementos a un HyperLogLog"""
        return await self.redis_client.pfadd(key, *elements)
    
    async def pfcount(self, key: str) -> int:
        """Cuenta elementos únicos en un HyperLogLog"""
        return await self.redis_client.pfcount(key)
    
    # Operaciones de Streams (para eventos)
    async def xadd(self, stream: str, fields: Dict[str, Any], id: str = "*") -> str:
        """Agrega un mensaje a un stream"""
        return await self.redis_client.xadd(stream, fields, id=id)
    
    async def xread(self, streams: Dict[str, str], count: Optional[int] = None, block: Optional[int] = None) -> List:
        """Lee mensajes de streams"""
        return await self.redis_client.xread(streams, count=count, block=block)
    
    # Operaciones avanzadas
    async def set_with_expiry(self, key: str, value: str, expire_seconds: int, only_if_not_exists: bool = False) -> bool:
        """Establece un valor con TTL y opción NX"""
        if only_if_not_exists:
            return await self.redis_client.set(key, value, ex=expire_seconds, nx=True) is not None
        return await self.redis_client.set(key, value, ex=expire_seconds)
    
    async def incr(self, key: str) -> int:
        """Incrementa un contador"""
        return await self.redis_client.incr(key)
    
    async def pipeline_execute(self, operations: List[tuple]) -> List:
        """Ejecuta múltiples operaciones en un pipeline"""
        pipe = self.redis_client.pipeline()
        
        for operation in operations:
            method_name, args, kwargs = operation
            method = getattr(pipe, method_name)
            method(*args, **kwargs)
        
        return await pipe.execute()
    
    # Utilidades para el sistema de cine
    async def get_sala_ocupacion(self, funcion_id: str) -> Dict[str, Any]:
        """Obtiene el estado de ocupación de una sala usando bitmap"""
        bitmap_key = f"sala:asientos:{funcion_id}"
        
        # Contar asientos ocupados
        ocupados = await self.bitcount(bitmap_key)
        
        # Obtener capacidad total (podría estar en otro hash)
        capacidad_total = await self.hget(f"funcion:{funcion_id}", "capacidad_total")
        capacidad_total = int(capacidad_total) if capacidad_total else 100  # default
        
        disponibles = capacidad_total - ocupados
        porcentaje_ocupacion = (ocupados / capacidad_total) * 100 if capacidad_total > 0 else 0
        
        return {
            "ocupados": ocupados,
            "disponibles": disponibles,
            "capacidad_total": capacidad_total,
            "porcentaje_ocupacion": round(porcentaje_ocupacion, 2)
        }
    
    async def get_ranking_peliculas(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtiene el ranking de películas más vendidas"""
        ranking = await self.zrange(
            "ranking:peliculas:ventas", 
            0, limite - 1, 
            desc=True, 
            withscores=True
        )
        
        resultado = []
        for i, (pelicula_id, ventas) in enumerate(ranking):
            resultado.append({
                "posicion": i + 1,
                "pelicula_id": pelicula_id,
                "ventas": int(ventas)
            })
        
        return resultado
    
    async def limpiar_reservas_vencidas(self):
        """Limpia reservas temporales vencidas (tarea programada)"""
        # Esta función sería llamada por un job scheduler
        pattern = "reserva:*"
        reservas = await self.redis_client.keys(pattern)
        
        reservas_eliminadas = 0
        for reserva_key in reservas:
            ttl = await self.redis_client.ttl(reserva_key)
            if ttl == -1:  # Sin TTL (no debería pasar)
                await self.delete(reserva_key)
                reservas_eliminadas += 1
        
        return reservas_eliminadas 