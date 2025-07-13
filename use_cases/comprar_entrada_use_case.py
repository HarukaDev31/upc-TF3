from typing import Dict, Any, List
from pydantic import BaseModel
from infrastructure.database.mongodb_service import MongoDBService
from infrastructure.cache.redis_service import RedisService
import uuid
from datetime import datetime


class CompraEntradaRequest(BaseModel):
    cliente_id: str
    pelicula_id: str
    funcion_id: str
    asientos: List[str]
    metodo_pago: str


class ComprarEntradaUseCase:
    """
    Caso de uso para comprar entradas
    Implementa la lógica de negocio optimizada
    """
    
    def __init__(self):
        self.mongodb_service = MongoDBService()
        self.redis_service = RedisService()
    
    async def ejecutar(self, request: CompraEntradaRequest) -> Dict[str, Any]:
        """
        Ejecuta el proceso de compra de entradas
        """
        try:
            # 1. Validar que la función existe
            funcion = await self.mongodb_service.obtener_funcion(request.funcion_id)
            if not funcion:
                raise ValueError("Función no encontrada")
            
            # 2. Verificar disponibilidad de asientos
            asientos_disponibles = await self._verificar_disponibilidad_asientos(
                request.funcion_id, request.asientos
            )
            
            if not asientos_disponibles:
                raise ValueError("Asientos no disponibles")
            
            # 3. Crear reserva temporal
            reserva_id = await self.redis_service.crear_reserva_temporal(
                request.funcion_id, request.asientos, 300  # 5 minutos
            )
            
            # 4. Procesar pago (simulado)
            resultado_pago = await self._procesar_pago(request)
            
            # 5. Crear transacción en MongoDB
            transaccion_data = {
                "_id": f"TRX_{request.cliente_id}_{request.funcion_id}_{uuid.uuid4().hex[:8]}",
                "cliente_id": request.cliente_id,
                "pelicula_id": request.pelicula_id,
                "funcion_id": request.funcion_id,
                "asientos": request.asientos,
                "metodo_pago": request.metodo_pago,
                "total": resultado_pago["total"],
                "estado": "confirmado",
                "fecha_creacion": datetime.now().isoformat(),
                "numero_factura": f"CIN-{request.funcion_id}-{uuid.uuid4().hex[:6].upper()}",
                "reserva_id": reserva_id
            }
            
            transaccion = await self.mongodb_service.guardar_transaccion(transaccion_data)
            
            # 6. Actualizar métricas en Redis
            await self._actualizar_metricas(request.pelicula_id, len(request.asientos))
            
            # 7. Generar QR code (simulado)
            qr_code = self._generar_qr_code(transaccion["_id"])
            
            return {
                "transaccion_id": transaccion["_id"],
                "estado": "confirmado",
                "asientos": request.asientos,
                "total": resultado_pago["total"],
                "qr_code": qr_code,
                "numero_factura": transaccion["numero_factura"]
            }
            
        except Exception as e:
            # En caso de error, liberar reserva temporal
            if 'reserva_id' in locals():
                await self.redis_service.delete(f"reserva:{reserva_id}")
            raise e
    
    async def _verificar_disponibilidad_asientos(self, funcion_id: str, asientos: List[str]) -> bool:
        """Verifica si los asientos están disponibles"""
        asientos_ocupados = await self.redis_service.get_asientos_ocupados(funcion_id)
        
        # Verificar que ningún asiento solicitado esté ocupado
        for asiento in asientos:
            if asiento in asientos_ocupados:
                return False
        
        return True
    
    async def _procesar_pago(self, request: CompraEntradaRequest) -> Dict[str, Any]:
        """Procesa el pago (simulado)"""
        # Calcular precio por asiento
        precio_por_asiento = 15000  # Precio base
        
        # Aplicar descuentos si aplica
        descuento = await self._calcular_descuento(request.cliente_id)
        precio_final = precio_por_asiento * (1 - descuento)
        
        total = precio_final * len(request.asientos)
        
        return {
            "total": total,
            "precio_por_asiento": precio_final,
            "descuento_aplicado": descuento
        }
    
    async def _calcular_descuento(self, cliente_id: str) -> float:
        """Calcula descuento basado en el tipo de cliente"""
        cliente = await self.mongodb_service.obtener_cliente(cliente_id)
        
        if not cliente:
            return 0.0
        
        tipo_cliente = cliente.get("tipo", "estandar")
        
        descuentos = {
            "vip": 0.15,      # 15% descuento
            "premium": 0.10,   # 10% descuento
            "estandar": 0.0    # Sin descuento
        }
        
        return descuentos.get(tipo_cliente, 0.0)
    
    async def _actualizar_metricas(self, pelicula_id: str, cantidad_asientos: int):
        """Actualiza métricas de ventas en Redis"""
        # Incrementar contador de ventas para la película
        await self.redis_service.zincrby("ranking:peliculas:ventas", cantidad_asientos, pelicula_id)
        
        # Incrementar contador de transacciones
        await self.redis_service.incr("metricas:transacciones:total")
    
    def _generar_qr_code(self, transaccion_id: str) -> str:
        """Genera QR code para la entrada (simulado)"""
        # En implementación real, usaría una librería como qrcode
        return f"data:image/png;base64,iVBORw0KGgoAAAANS...{transaccion_id[:10]}" 