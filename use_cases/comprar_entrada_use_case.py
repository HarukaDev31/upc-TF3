"""
Caso de uso para comprar entradas
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from domain.entities.transaccion import Transaccion, DetalleAsiento, DetallePago, MetodoPago, EstadoTransaccion
from domain.entities.usuario import Usuario, UsuarioResponse
from domain.repositories.transaccion_repository import TransaccionRepository
from domain.repositories.usuario_repository import UsuarioRepository
from infrastructure.database.mongodb_service import MongoDBService
from domain.repositories.seleccion_asiento_repository import SeleccionAsientoRepository
from services.global_services import get_mongodb_service
from infrastructure.cache.redis_service import RedisService
from services.email_service import email_service
import asyncio


class ComprarEntradaUseCase:
    """Caso de uso para comprar entradas"""
    
    def __init__(self):
        self.mongodb_service = get_mongodb_service()
        self.redis_service = RedisService()
        
        if self.mongodb_service:
            self.transaccion_repo = TransaccionRepository(self.mongodb_service.database)
            self.usuario_repo = UsuarioRepository(self.mongodb_service.database)
            self.seleccion_repo = SeleccionAsientoRepository(self.mongodb_service.database)
    
    async def ejecutar(
        self,
        usuario_id: str,
        funcion_id: str,
        asientos: List[str],
        metodo_pago: MetodoPago,
        datos_pago: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Ejecutar la compra de entradas"""
        
        try:
            # 1. Validar que el usuario existe
            usuario = await self.usuario_repo.obtener_usuario_por_id(usuario_id)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # 2. Validar que la función existe
            funcion = await self.mongodb_service.obtener_funcion(funcion_id)
            if not funcion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Función no encontrada"
                )
            
            # 3. Validar que los asientos están disponibles
            asientos_disponibles = await self._verificar_disponibilidad_asientos(funcion_id, asientos)
            if not asientos_disponibles:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Uno o más asientos no están disponibles"
                )
            
            # 4. Obtener información de la película
            pelicula = await self.mongodb_service.obtener_pelicula(funcion.get("pelicula_id"))
            
            # 5. Crear detalles de asientos
            detalles_asientos = await self._crear_detalles_asientos(asientos, funcion_id)
            
            # 6. Crear detalle de pago
            detalle_pago = self._crear_detalle_pago(metodo_pago, datos_pago)
            
            # 7. Crear transacción con totales calculados
            # Calcular subtotal antes de crear la transacción
            subtotal = sum(asiento.precio_unitario for asiento in detalles_asientos)
            cantidad_asientos = len(detalles_asientos)
            
            # Calcular impuestos (19% IVA)
            impuestos = subtotal * 0.19
            
            # Total inicial (sin descuentos)
            total = subtotal + impuestos
            
            transaccion = Transaccion(
                cliente_id=usuario_id,
                pelicula_id=funcion.get("pelicula_id"),
                funcion_id=funcion_id,
                asientos=detalles_asientos,
                pago=detalle_pago,
                subtotal=subtotal,
                cantidad_asientos=cantidad_asientos,
                total=total,
                impuestos=impuestos,
                fecha_vencimiento=datetime.now() + timedelta(minutes=30),  # 30 minutos para pagar
                ip_origen=datos_pago.get("ip_origen") if datos_pago else None,
                user_agent=datos_pago.get("user_agent") if datos_pago else None,
                canal_venta=datos_pago.get("canal_venta", "web") if datos_pago else "web"
            )
            
            # 8. Aplicar descuentos y recalcular totales
            await self._aplicar_descuentos(transaccion, usuario)
            transaccion.calcular_totales()
            
            # 9. Aplicar descuentos si corresponde
            await self._aplicar_descuentos(transaccion, usuario)
            
            # 10. Guardar transacción
            transaccion_creada = await self.transaccion_repo.crear_transaccion(transaccion)
            if not transaccion_creada:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear la transacción"
                )
            
            # 11. Confirmar selecciones temporales (se marcarán como confirmadas después del pago)
            await self._confirmar_selecciones_temporales(usuario_id, funcion_id, asientos)
            
            # 12. Procesar pago (simulado)
            resultado_pago = await self._procesar_pago(transaccion_creada)
            
            # 13. Actualizar estado según resultado del pago
            if resultado_pago["exitoso"]:
                await self.transaccion_repo.actualizar_estado_transaccion(
                    transaccion_creada.id,
                    EstadoTransaccion.CONFIRMADO,
                    f"Pago procesado exitosamente. Código: {resultado_pago['codigo_autorizacion']}"
                )
                estado_final = EstadoTransaccion.CONFIRMADO
                
                # 13.1. Confirmar selecciones temporales
                try:
                    await self._confirmar_selecciones_temporales(usuario_id, funcion_id, asientos)
                    print(f"✅ Selecciones temporales confirmadas para asientos: {asientos}")
                except Exception as e:
                    print(f"⚠️  Error confirmando selecciones temporales: {e}")
                
                # 13.2. Marcar asientos como ocupados en la función
                try:
                    await self._marcar_asientos_ocupados(funcion_id, asientos)
                    print(f"✅ Asientos marcados como ocupados: {asientos}")
                except Exception as e:
                    print(f"⚠️  Error marcando asientos como ocupados: {e}")
                    # No fallar la transacción por error al marcar asientos
                
                # 13.3. Enviar correo de confirmación usando Redis
                try:
                    # Preparar datos para el correo
                    transaccion_data = {
                        "transaccion_id": transaccion_creada.id,
                        "numero_factura": transaccion_creada.numero_factura,
                        "estado": estado_final,
                        "total": transaccion_creada.total,
                        "asientos": asientos,
                        "fecha_vencimiento": transaccion_creada.fecha_vencimiento.isoformat(),
                        "resultado_pago": resultado_pago,
                        "resumen": transaccion_creada.generar_resumen(),
                        "codigo_qr": transaccion_creada.id  # O el QR real si lo tienes
                    }
                    
                    # Enviar correo de confirmación
                    await email_service.enviar_correo_confirmacion_compra(
                        email=usuario.email,
                        transaccion_data=transaccion_data
                    )
                    
                except Exception as e:
                    print(f"⚠️  Error enviando correo de confirmación: {e}")
                    # No fallar la transacción por error de correo
                
            else:
                await self.transaccion_repo.actualizar_estado_transaccion(
                    transaccion_creada.id,
                    EstadoTransaccion.FALLIDO,
                    f"Error en el pago: {resultado_pago['mensaje']}"
                )
                estado_final = EstadoTransaccion.FALLIDO
                
                # Si el pago falla, liberar las selecciones temporales
                try:
                    await self._liberar_selecciones_temporales(usuario_id, funcion_id, asientos)
                    print(f"⚠️  Selecciones temporales liberadas por pago fallido: {asientos}")
                except Exception as e:
                    print(f"⚠️  Error liberando selecciones temporales: {e}")
            
            # 14. Generar respuesta
            return {
                "transaccion_id": transaccion_creada.id,
                "numero_factura": transaccion_creada.numero_factura,
                "estado": estado_final,
                "total": transaccion_creada.total,
                "asientos": asientos,
                "fecha_vencimiento": transaccion_creada.fecha_vencimiento.isoformat(),
                "resultado_pago": resultado_pago,
                "resumen": transaccion_creada.generar_resumen()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )
    
    async def _verificar_disponibilidad_asientos(self, funcion_id: str, asientos: List[str]) -> bool:
        """Verificar que los asientos están disponibles"""
        try:
            # Verificar en transacciones confirmadas
            asientos_disponibles = await self.transaccion_repo.verificar_asientos_disponibles(funcion_id, asientos)
            if not asientos_disponibles:
                return False
            
            # Verificar en Redis (selecciones temporales)
            asientos_ocupados_redis = await self.redis_service.get_asientos_ocupados(funcion_id)
            for asiento in asientos:
                if asiento in asientos_ocupados_redis:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error verificando disponibilidad: {e}")
            return False
    
    async def _crear_detalles_asientos(self, asientos: List[str], funcion_id: str) -> List[DetalleAsiento]:
        """Crear detalles de asientos con precios"""
        detalles = []
        
        for asiento_codigo in asientos:
            # Extraer fila y número del código (ej: "A1" -> fila="A", numero=1)
            fila = asiento_codigo[0]
            numero = int(asiento_codigo[1:])
            
            # Determinar tipo y precio según la fila
            if fila in ["A", "B"]:
                tipo = "vip"
                precio_unitario = 25000
            else:
                tipo = "estandar"
                precio_unitario = 18000
            
            detalle = DetalleAsiento(
                codigo=asiento_codigo,
                fila=fila,
                numero=numero,
                tipo=tipo,
                precio_unitario=precio_unitario,
                precio_final=precio_unitario  # Se actualizará al calcular totales
            )
            
            detalles.append(detalle)
        
        return detalles
    
    def _crear_detalle_pago(self, metodo_pago: MetodoPago, datos_pago: Dict[str, Any] = None) -> DetallePago:
        """Crear detalle de pago"""
        datos_pago = datos_pago or {}
        
        return DetallePago(
            metodo=metodo_pago,
            referencia_externa=datos_pago.get("referencia_externa"),
            ultimos_4_digitos=datos_pago.get("ultimos_4_digitos"),
            banco_emisor=datos_pago.get("banco_emisor"),
            tasa_procesamiento=datos_pago.get("tasa_procesamiento", 0.0),
            monto_procesamiento=datos_pago.get("monto_procesamiento", 0.0)
        )
    
    async def _aplicar_descuentos(self, transaccion: Transaccion, usuario: UsuarioResponse) -> None:
        """Aplicar descuentos según el tipo de usuario"""
        # Ejemplo: descuento del 10% para usuarios VIP
        # En un sistema real, esto se basaría en el historial de compras
        if usuario.email.endswith("@vip.com"):
            transaccion.aplicar_descuento_cliente(0.10)
        
        # Descuento promocional si hay código
        codigo_promocion = transaccion.datos_adicionales.get("codigo_promocion")
        if codigo_promocion == "CINE2024":
            transaccion.aplicar_descuento_promocional(0.05, codigo_promocion)
    
    async def _confirmar_selecciones_temporales(self, usuario_id: str, funcion_id: str, asientos: List[str]) -> None:
        """Confirmar selecciones temporales del usuario (pago exitoso)"""
        try:
            from datetime import datetime
            
            # Marcar como confirmadas en la base de datos
            for asiento in asientos:
                await self.seleccion_repo.actualizar_estado_seleccion(
                    usuario_id, funcion_id, asiento, "confirmada", datetime.now()
                )
            
            # Liberar de Redis (ya no son temporales)
            for asiento in asientos:
                await self.redis_service.liberar_asiento(funcion_id, asiento, usuario_id)
                
            print(f"✅ Selecciones confirmadas para usuario {usuario_id}, asientos: {asientos}")
                
        except Exception as e:
            print(f"❌ Error confirmando selecciones temporales: {e}")
            raise
    
    async def _liberar_selecciones_temporales(self, usuario_id: str, funcion_id: str, asientos: List[str]) -> None:
        """Liberar selecciones temporales del usuario (pago fallido)"""
        try:
            from datetime import datetime
            
            # Marcar como canceladas en la base de datos
            for asiento in asientos:
                await self.seleccion_repo.actualizar_estado_seleccion(
                    usuario_id, funcion_id, asiento, "cancelada", datetime.now()
                )
            
            # Liberar de Redis
            for asiento in asientos:
                await self.redis_service.liberar_asiento(funcion_id, asiento, usuario_id)
                
            print(f"⚠️  Selecciones liberadas para usuario {usuario_id}, asientos: {asientos}")
                
        except Exception as e:
            print(f"❌ Error liberando selecciones temporales: {e}")
            raise
    
    async def _limpiar_selecciones_temporales(self, usuario_id: str, funcion_id: str, asientos: List[str]) -> None:
        """Limpiar selecciones temporales del usuario (método legacy)"""
        try:
            # Eliminar de Redis
            for asiento in asientos:
                await self.redis_service.liberar_asiento(funcion_id, asiento, usuario_id)
            
            # Eliminar de base de datos
            for asiento in asientos:
                await self.seleccion_repo.eliminar_seleccion_usuario_asiento(
                    usuario_id, funcion_id, asiento
                )
                
        except Exception as e:
            print(f"Error limpiando selecciones temporales: {e}")
    
    async def _procesar_pago(self, transaccion: Transaccion) -> Dict[str, Any]:
        """Procesar el pago (simulado)"""
        try:
            # Simular procesamiento de pago
            import random
            import time
            
            # Simular delay de procesamiento
            await asyncio.sleep(1)
            
            # Simular éxito/fallo (90% éxito)
            exito = random.random() < 0.9
            
            if exito:
                codigo_autorizacion = f"AUTH{int(time.time())}{random.randint(1000, 9999)}"
                return {
                    "exitoso": True,
                    "codigo_autorizacion": codigo_autorizacion,
                    "mensaje": "Pago procesado exitosamente",
                    "fecha_procesamiento": datetime.now().isoformat()
                }
            else:
                return {
                    "exitoso": False,
                    "mensaje": "Tarjeta rechazada - fondos insuficientes",
                    "fecha_procesamiento": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "exitoso": False,
                "mensaje": f"Error procesando pago: {str(e)}",
                "fecha_procesamiento": datetime.now().isoformat()
            }
    
    async def _marcar_asientos_ocupados(self, funcion_id: str, asientos: List[str]) -> None:
        """Marcar asientos como ocupados en la función"""
        try:
            # Obtener la función actual
            funcion = await self.mongodb_service.obtener_funcion(funcion_id)
            if not funcion:
                raise Exception(f"Función {funcion_id} no encontrada")
            
            # Actualizar asientos ocupados en la función
            asientos_ocupados_actuales = funcion.get("asientos_ocupados", [])
            asientos_ocupados_actuales.extend(asientos)
            
            # Actualizar en MongoDB
            await self.mongodb_service.actualizar_funcion(
                funcion_id,
                {"asientos_ocupados": asientos_ocupados_actuales}
            )
            
            # También marcar como ocupados en Redis para consistencia
            for asiento in asientos:
                await self.redis_service.marcar_asiento_ocupado(funcion_id, asiento)
            
            print(f"✅ Asientos {asientos} marcados como ocupados en función {funcion_id}")
            
        except Exception as e:
            print(f"❌ Error marcando asientos como ocupados: {e}")
            raise
    
    async def obtener_historial_compras(self, usuario_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtener historial de compras del usuario"""
        try:
            transacciones = await self.transaccion_repo.obtener_transacciones_por_cliente(usuario_id, limit)
            
            historial = []
            for transaccion in transacciones:
                historial.append({
                    "id": transaccion.id,
                    "numero_factura": transaccion.numero_factura,
                    "fecha": transaccion.fecha_creacion.isoformat(),
                    "funcion_id": transaccion.funcion_id,
                    "asientos": transaccion.obtener_codigos_asientos(),
                    "total": transaccion.total,
                    "estado": transaccion.estado,
                    "metodo_pago": transaccion.pago.metodo
                })
            
            return historial
            
        except Exception as e:
            print(f"Error obteniendo historial de compras: {e}")
            return []
    
    async def cancelar_transaccion(self, transaccion_id: str, usuario_id: str) -> Dict[str, Any]:
        """Cancelar una transacción"""
        try:
            transaccion = await self.transaccion_repo.obtener_transaccion_por_id(transaccion_id)
            
            if not transaccion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transacción no encontrada"
                )
            
            if transaccion.cliente_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para cancelar esta transacción"
                )
            
            if not transaccion.puede_ser_cancelada():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La transacción no puede ser cancelada"
                )
            
            # Actualizar estado
            await self.transaccion_repo.actualizar_estado_transaccion(
                transaccion_id,
                EstadoTransaccion.CANCELADO,
                "Transacción cancelada por el usuario"
            )
            
            return {
                "mensaje": "Transacción cancelada exitosamente",
                "transaccion_id": transaccion_id,
                "estado": EstadoTransaccion.CANCELADO
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error cancelando transacción: {str(e)}"
            ) 