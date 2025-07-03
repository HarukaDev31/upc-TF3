from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class EstadoTransaccion(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    CONFIRMADO = "confirmado"
    FALLIDO = "fallido"
    REEMBOLSADO = "reembolsado"
    CANCELADO = "cancelado"


class MetodoPago(str, Enum):
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    PUNTOS = "puntos"


class DetalleAsiento(BaseModel):
    codigo: str = Field(..., min_length=1)
    fila: str = Field(..., min_length=1, max_length=2)
    numero: int = Field(..., gt=0)
    tipo: str = Field(default="estandar")
    precio_unitario: float = Field(..., gt=0)
    descuento_aplicado: float = Field(default=0.0, ge=0)
    precio_final: float = Field(..., gt=0)


class DetallePago(BaseModel):
    metodo: MetodoPago
    referencia_externa: Optional[str] = None
    ultimos_4_digitos: Optional[str] = Field(None, min_length=4, max_length=4)
    banco_emisor: Optional[str] = None
    fecha_procesamiento: Optional[datetime] = None
    codigo_autorizacion: Optional[str] = None
    tasa_procesamiento: float = Field(default=0.0, ge=0)
    monto_procesamiento: float = Field(default=0.0, ge=0)


class Transaccion(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    cliente_id: str = Field(..., min_length=1)
    pelicula_id: str = Field(..., min_length=1)
    funcion_id: str = Field(..., min_length=1)
    
    # Detalles de asientos
    asientos: List[DetalleAsiento] = Field(..., min_items=1)
    cantidad_asientos: int = Field(..., gt=0)
    
    # Información financiera
    subtotal: float = Field(..., gt=0)
    descuento_cliente: float = Field(default=0.0, ge=0)
    descuento_promocional: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    total: float = Field(..., gt=0)
    
    # Detalles de pago
    pago: DetallePago
    
    # Estado y timestamps
    estado: EstadoTransaccion = EstadoTransaccion.PENDIENTE
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    fecha_vencimiento: Optional[datetime] = None
    fecha_confirmacion: Optional[datetime] = None
    
    # Metadata adicional
    codigo_qr: Optional[str] = None
    numero_factura: Optional[str] = None
    observaciones: Optional[str] = None
    datos_adicionales: Dict[str, Any] = Field(default_factory=dict)
    
    # Auditoría
    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None
    canal_venta: str = Field(default="web")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.numero_factura:
            self.numero_factura = self.generar_numero_factura()

    def generar_numero_factura(self) -> str:
        """Genera un número de factura único"""
        timestamp = self.fecha_creacion.strftime("%Y%m%d%H%M%S")
        return f"CIN-{timestamp}-{str(uuid.uuid4())[:8].upper()}"

    def calcular_totales(self) -> None:
        """Recalcula todos los totales basado en los asientos"""
        self.subtotal = sum(asiento.precio_unitario for asiento in self.asientos)
        self.cantidad_asientos = len(self.asientos)
        
        # Calcular descuentos
        descuento_total = self.descuento_cliente + self.descuento_promocional
        subtotal_con_descuento = self.subtotal * (1 - descuento_total)
        
        # Calcular impuestos (ejemplo: 19% IVA)
        self.impuestos = subtotal_con_descuento * 0.19
        
        # Total final
        self.total = subtotal_con_descuento + self.impuestos
        
        # Actualizar precio final de cada asiento
        factor_descuento = 1 - descuento_total
        for asiento in self.asientos:
            asiento.descuento_aplicado = descuento_total
            asiento.precio_final = asiento.precio_unitario * factor_descuento

    def puede_ser_cancelada(self) -> bool:
        """Verifica si la transacción puede ser cancelada"""
        estados_cancelables = [
            EstadoTransaccion.PENDIENTE,
            EstadoTransaccion.PROCESANDO
        ]
        return self.estado in estados_cancelables

    def puede_ser_reembolsada(self) -> bool:
        """Verifica si la transacción puede ser reembolsada"""
        return self.estado == EstadoTransaccion.CONFIRMADO

    def esta_vencida(self) -> bool:
        """Verifica si la transacción está vencida"""
        if not self.fecha_vencimiento:
            return False
        return datetime.now() > self.fecha_vencimiento

    def marcar_como_confirmada(self) -> None:
        """Marca la transacción como confirmada"""
        self.estado = EstadoTransaccion.CONFIRMADO
        self.fecha_confirmacion = datetime.now()
        self.fecha_actualizacion = datetime.now()

    def marcar_como_fallida(self, motivo: str = None) -> None:
        """Marca la transacción como fallida"""
        self.estado = EstadoTransaccion.FALLIDO
        self.fecha_actualizacion = datetime.now()
        if motivo:
            self.observaciones = motivo

    def aplicar_descuento_cliente(self, porcentaje: float) -> None:
        """Aplica un descuento basado en el tipo de cliente"""
        self.descuento_cliente = max(0.0, min(1.0, porcentaje))
        self.calcular_totales()

    def aplicar_descuento_promocional(self, porcentaje: float, codigo_promocion: str = None) -> None:
        """Aplica un descuento promocional"""
        self.descuento_promocional = max(0.0, min(1.0, porcentaje))
        if codigo_promocion:
            self.datos_adicionales["codigo_promocion"] = codigo_promocion
        self.calcular_totales()

    def generar_resumen(self) -> Dict[str, Any]:
        """Genera un resumen de la transacción para mostrar al usuario"""
        return {
            "id": self.id,
            "numero_factura": self.numero_factura,
            "fecha": self.fecha_creacion.isoformat(),
            "cliente_id": self.cliente_id,
            "asientos": [
                {
                    "codigo": asiento.codigo,
                    "precio": asiento.precio_final
                }
                for asiento in self.asientos
            ],
            "subtotal": self.subtotal,
            "descuentos": self.descuento_cliente + self.descuento_promocional,
            "impuestos": self.impuestos,
            "total": self.total,
            "metodo_pago": self.pago.metodo,
            "estado": self.estado
        }

    def obtener_codigos_asientos(self) -> List[str]:
        """Retorna una lista con los códigos de todos los asientos"""
        return [asiento.codigo for asiento in self.asientos]

    def actualizar_estado(self, nuevo_estado: EstadoTransaccion, observacion: str = None) -> None:
        """Actualiza el estado de la transacción"""
        self.estado = nuevo_estado
        self.fecha_actualizacion = datetime.now()
        
        if observacion:
            if self.observaciones:
                self.observaciones += f" | {observacion}"
            else:
                self.observaciones = observacion 