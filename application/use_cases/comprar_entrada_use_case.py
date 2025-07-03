from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime, timedelta

from domain.entities.cliente import Cliente
from domain.entities.funcion import Funcion
from domain.entities.transaccion import Transaccion, DetalleAsiento, DetallePago, EstadoTransaccion
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.funcion_repository import FuncionRepository
from infrastructure.cache.redis_service import RedisService
from infrastructure.database.mongodb_service import MongoDBService
from infrastructure.external.payment_service import PaymentService
from infrastructure.utils.qr_generator import QRGenerator


class DatosCompra:
    """DTO para los datos de compra de entrada"""
    def __init__(self, cliente_id: str, pelicula_id: str, funcion_id: str, asientos: List[str], metodo_pago: str):
        self.cliente_id = cliente_id
        self.pelicula_id = pelicula_id
        self.funcion_id = funcion_id
        self.asientos = asientos
        self.metodo_pago = metodo_pago


class ComprarEntradaUseCase:
    """
    Caso de uso principal para compra de entradas
    Implementa el algoritmo optimizado con Redis y MongoDB
    Complejidad: O(log n) para la mayoría de operaciones
    """
    
    def __init__(
        self,
        cliente_repository: ClienteRepository,
        funcion_repository: FuncionRepository,
        redis_service: RedisService,
        mongodb_service: MongoDBService,
        payment_service: PaymentService,
        qr_generator: QRGenerator
    ):
        self.cliente_repository = cliente_repository
        self.funcion_repository = funcion_repository
        self.redis_service = redis_service
        self.mongodb_service = mongodb_service
        self.payment_service = payment_service
        self.qr_generator = qr_generator

    async def ejecutar(self, datos_compra: DatosCompra) -> Dict[str, Any]:
        """
        Algoritmo principal de compra implementando estructuras de datos óptimas
        Complejidad: O(log n) para la mayoría de operaciones
        """
        
        # PASO 1: Validación y Cache Check (Redis) - O(1)
        cliente = await self._validar_y_obtener_cliente(datos_compra.cliente_id)
        funcion = await self._obtener_funcion(datos_compra.funcion_id)
        
        if not funcion.esta_en_horario_venta():
            raise ValueError("La función ya no está disponible para venta")
        
        # PASO 2: Verificar disponibilidad con Bitmaps (Redis) - O(k)
        asientos_disponibles = await self._verificar_disponibilidad_asientos(
            datos_compra.funcion_id, datos_compra.asientos
        )
        
        # PASO 3: Reserva temporal con Lock distribuido - O(k)
        reserva_id = await self._crear_reserva_temporal(
            datos_compra, asientos_disponibles
        )
        
        try:
            # PASO 4: Procesar pago y persistir en MongoDB - O(1)
            transaccion = await self._crear_transaccion(
                datos_compra, asientos_disponibles, cliente, funcion
            )
            
            # Simular procesamiento de pago
            pago_exitoso = await self._procesar_pago_async(transaccion)
            
            if pago_exitoso:
                # PASO 5: Confirmar transacción
                return await self._confirmar_transaccion(transaccion, datos_compra)
            else:
                # PASO 6: Rollback en caso de fallo
                await self._rollback_reserva(datos_compra.funcion_id, asientos_disponibles, reserva_id)
                raise ValueError("Error en el procesamiento del pago")
                
        except Exception as e:
            # Rollback automático en caso de cualquier error
            await self._rollback_reserva(datos_compra.funcion_id, asientos_disponibles, reserva_id)
            raise e

    async def _validar_y_obtener_cliente(self, cliente_id: str) -> Cliente:
        """Validación y Cache Check (Redis) - O(1)"""
        cliente_cache_key = f"cliente:{cliente_id}"
        
        # Verificar en cache si cliente existe
        cliente_data = await self.redis_service.hgetall(cliente_cache_key)
        
        if not cliente_data:
            # Si no está en cache, buscar en MongoDB
            cliente = await self.cliente_repository.obtener_por_id(cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            
            # Guardar en cache con TTL de 1 hora
            await self.redis_service.hset(cliente_cache_key, {
                "nombre": cliente.nombre,
                "email": cliente.email,
                "tipo": cliente.tipo.value
            })
            await self.redis_service.expire(cliente_cache_key, 3600)
            return cliente
        else:
            # Reconstruir cliente desde cache
            return Cliente(
                id=cliente_id,
                nombre=cliente_data["nombre"],
                email=cliente_data["email"],
                tipo=cliente_data["tipo"]
            )

    async def _obtener_funcion(self, funcion_id: str) -> Funcion:
        """Obtiene información de la función"""
        funcion = await self.funcion_repository.obtener_por_id(funcion_id)
        if not funcion:
            raise ValueError("Función no encontrada")
        return funcion

    async def _verificar_disponibilidad_asientos(self, funcion_id: str, asientos_solicitados: List[str]) -> List[str]:
        """Verificar disponibilidad con Bitmaps (Redis) - O(k)"""
        bitmap_key = f"sala:asientos:{funcion_id}"
        asientos_disponibles = []
        
        # Pipeline para verificar múltiples asientos
        for asiento in asientos_solicitados:
            # Convertir asiento (ej: "A5") a posición de bit
            bit_position = self._asiento_to_bit_position(asiento)
            ocupado = await self.redis_service.getbit(bitmap_key, bit_position)
            
            # Verificar que el asiento esté disponible (bit = 0)
            if ocupado == 0:
                asientos_disponibles.append(asiento)
            else:
                raise ValueError(f"Asiento {asiento} no disponible")
        
        return asientos_disponibles

    async def _crear_reserva_temporal(self, datos_compra: DatosCompra, asientos_disponibles: List[str]) -> str:
        """Reserva temporal con Lock distribuido - O(k)"""
        lock_key = f"lock:funcion:{datos_compra.funcion_id}"
        reserva_id = f"reserva:{datos_compra.cliente_id}:{datos_compra.funcion_id}:{datetime.now().timestamp()}"
        
        # Adquirir lock con Redlock algorithm
        lock_acquired = await self.redis_service.set_with_expiry(
            lock_key, reserva_id, expire_seconds=5, only_if_not_exists=True
        )
        
        if not lock_acquired:
            # Reintentar con backoff exponencial
            await asyncio.sleep(0.1)
            lock_acquired = await self.redis_service.set_with_expiry(
                lock_key, reserva_id, expire_seconds=5, only_if_not_exists=True
            )
            if not lock_acquired:
                raise ValueError("Sistema ocupado, intente nuevamente")
        
        try:
            # Marcar asientos como reservados temporalmente
            bitmap_key = f"sala:asientos:{datos_compra.funcion_id}"
            for asiento in asientos_disponibles:
                bit_position = self._asiento_to_bit_position(asiento)
                await self.redis_service.setbit(bitmap_key, bit_position, 1)
            
            # Crear reserva temporal en Redis con TTL
            reserva_data = {
                "cliente_id": datos_compra.cliente_id,
                "funcion_id": datos_compra.funcion_id,
                "asientos": json.dumps(asientos_disponibles),
                "timestamp": datetime.now().isoformat(),
                "estado": "pendiente"
            }
            
            await self.redis_service.hset(f"reserva:{reserva_id}", reserva_data)
            await self.redis_service.expire(f"reserva:{reserva_id}", 600)  # 10 minutos
            
        finally:
            # Liberar lock
            await self.redis_service.delete(lock_key)
        
        return reserva_id

    async def _crear_transaccion(self, datos_compra: DatosCompra, asientos_disponibles: List[str], 
                                cliente: Cliente, funcion: Funcion) -> Transaccion:
        """Crear objeto transacción con todos los detalles"""
        
        # Crear detalles de asientos
        detalles_asientos = []
        for asiento in asientos_disponibles:
            precio = funcion.calcular_precio_asiento(asiento)
            detalle = DetalleAsiento(
                codigo=asiento,
                fila=asiento[0],
                numero=int(asiento[1:]),
                precio_unitario=precio,
                precio_final=precio
            )
            detalles_asientos.append(detalle)
        
        # Crear detalle de pago
        detalle_pago = DetallePago(
            metodo=datos_compra.metodo_pago
        )
        
        # Crear transacción
        transaccion = Transaccion(
            cliente_id=cliente.id,
            pelicula_id=datos_compra.pelicula_id,
            funcion_id=datos_compra.funcion_id,
            asientos=detalles_asientos,
            cantidad_asientos=len(asientos_disponibles),
            subtotal=sum(d.precio_unitario for d in detalles_asientos),
            total=0,  # Se calculará en calcular_totales
            pago=detalle_pago,
            estado=EstadoTransaccion.PROCESANDO
        )
        
        # Aplicar descuentos
        descuento_cliente = cliente.calcular_descuento()
        transaccion.aplicar_descuento_cliente(descuento_cliente)
        
        return transaccion

    async def _procesar_pago_async(self, transaccion: Transaccion) -> bool:
        """Simular procesamiento de pago asíncrono"""
        try:
            resultado = await self.payment_service.procesar_pago(
                monto=transaccion.total,
                metodo=transaccion.pago.metodo,
                referencia=transaccion.id
            )
            return resultado.exitoso
        except Exception:
            return False

    async def _confirmar_transaccion(self, transaccion: Transaccion, datos_compra: DatosCompra) -> Dict[str, Any]:
        """Confirmar transacción y actualizar métricas"""
        
        # Marcar transacción como confirmada
        transaccion.marcar_como_confirmada()
        
        # Guardar en MongoDB
        await self.mongodb_service.guardar_transaccion(transaccion)
        
        # Confirmar asientos en la función
        await self.funcion_repository.confirmar_asientos(
            datos_compra.funcion_id, 
            transaccion.obtener_codigos_asientos()
        )
        
        # Actualizar métricas en Redis
        await self._actualizar_metricas(
            datos_compra.pelicula_id, 
            datos_compra.funcion_id, 
            len(transaccion.asientos)
        )
        
        # Publicar evento en Redis Streams
        await self._publicar_evento_venta(transaccion)
        
        # Actualizar grafo de recomendaciones
        await self._actualizar_grafo_recomendaciones(
            datos_compra.cliente_id, 
            datos_compra.pelicula_id
        )
        
        # Generar QR
        codigo_qr = await self.qr_generator.generar(transaccion.id)
        
        return {
            "transaccion_id": transaccion.id,
            "estado": "confirmado",
            "asientos": transaccion.obtener_codigos_asientos(),
            "total": transaccion.total,
            "qr_code": codigo_qr,
            "numero_factura": transaccion.numero_factura
        }

    async def _rollback_reserva(self, funcion_id: str, asientos: List[str], reserva_id: str):
        """Rollback en caso de fallo"""
        # Liberar asientos en bitmap
        bitmap_key = f"sala:asientos:{funcion_id}"
        for asiento in asientos:
            bit_position = self._asiento_to_bit_position(asiento)
            await self.redis_service.setbit(bitmap_key, bit_position, 0)
        
        # Eliminar reserva temporal
        await self.redis_service.delete(f"reserva:{reserva_id}")

    async def _actualizar_metricas(self, pelicula_id: str, funcion_id: str, cantidad: int):
        """Actualiza métricas en tiempo real usando Redis"""
        # Incrementar contador de ventas
        await self.redis_service.hincrby(f"metricas:pelicula:{pelicula_id}", "ventas_total", cantidad)
        
        # Actualizar ranking en Sorted Set
        await self.redis_service.zincrby("ranking:peliculas:ventas", cantidad, pelicula_id)
        
        # Agregar a HyperLogLog para conteo de usuarios únicos
        await self.redis_service.pfadd(f"audiencia:pelicula:{pelicula_id}", funcion_id)

    async def _publicar_evento_venta(self, transaccion: Transaccion):
        """Publica evento de venta en Redis Streams"""
        evento = {
            "tipo": "venta_confirmada",
            "transaccion_id": transaccion.id,
            "cliente_id": transaccion.cliente_id,
            "pelicula_id": transaccion.pelicula_id,
            "monto": transaccion.total,
            "timestamp": datetime.now().isoformat()
        }
        await self.redis_service.xadd("stream:ventas", evento)

    async def _actualizar_grafo_recomendaciones(self, cliente_id: str, pelicula_id: str):
        """Actualiza grafo de recomendaciones para machine learning"""
        # Obtener historial del cliente
        historial_key = f"historial:cliente:{cliente_id}"
        peliculas_vistas = await self.redis_service.zrange(historial_key, 0, -1)
        
        # Actualizar pesos en el grafo
        for pelicula_vista in peliculas_vistas:
            edge_key = f"grafo:edge:{pelicula_vista}:{pelicula_id}"
            await self.redis_service.incr(edge_key)
        
        # Agregar nueva película al historial
        await self.redis_service.zadd(historial_key, {pelicula_id: datetime.now().timestamp()})

    def _asiento_to_bit_position(self, asiento: str) -> int:
        """Convierte asiento (ej: "A5") a posición de bit para Redis bitmap"""
        fila = ord(asiento[0].upper()) - ord('A')
        numero = int(asiento[1:])
        return (fila * 20) + numero  # Asumiendo 20 asientos por fila 