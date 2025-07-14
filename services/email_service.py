"""
Servicio de correo electrónico usando Redis
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from infrastructure.cache.redis_service import RedisService
from config.settings import settings


class EmailService:
    """Servicio de correo electrónico usando Redis Streams"""
    
    def __init__(self):
        self.redis_service = RedisService()
        self.email_stream = "email:notifications"
        self.email_queue = "email:queue"
    
    async def connect(self):
        """Conectar al servicio de Redis"""
        try:
            await self.redis_service.connect()
            print("✅ EmailService conectado a Redis")
        except Exception as e:
            print(f"❌ Error conectando EmailService a Redis: {e}")
            # Crear un cliente de Redis básico si falla
            self.redis_service.redis_client = None
    
    async def enviar_correo_confirmacion_compra(
        self, 
        email: str, 
        transaccion_data: Dict[str, Any]
    ) -> bool:
        """
        Envía correo de confirmación de compra usando Redis
        
        Args:
            email: Email del usuario
            transaccion_data: Datos de la transacción completada
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Verificar conexión a Redis
            if not self.redis_service.redis_client:
                print("⚠️  Redis no disponible, enviando correo directamente")
                # Enviar correo real directamente
                return await self._enviar_correo_real({
                    "to": email,
                    "subject": f"Confirmación de Compra - {transaccion_data.get('numero_factura', 'N/A')}",
                    "template": "confirmacion_compra",
                    "data": transaccion_data
                })
            
            # Crear mensaje de correo
            email_data = {
                "to": email,
                "subject": f"Confirmación de Compra - {transaccion_data.get('numero_factura', 'N/A')}",
                "template": "confirmacion_compra",
                "data": {
                    "transaccion_id": transaccion_data.get("transaccion_id"),
                    "numero_factura": transaccion_data.get("numero_factura"),
                    "fecha_compra": datetime.now().isoformat(),
                    "asientos": transaccion_data.get("asientos", []),
                    "total": transaccion_data.get("total", 0),
                    "metodo_pago": transaccion_data.get("resumen", {}).get("metodo_pago", "N/A"),
                    "estado": transaccion_data.get("estado", "confirmado"),
                    "fecha_vencimiento": transaccion_data.get("fecha_vencimiento"),
                    "codigo_qr": transaccion_data.get("codigo_qr", "QR-CODE")
                },
                "priority": "high",
                "timestamp": datetime.now().isoformat()
            }
            
            # Enviar a Redis Stream para procesamiento asíncrono
            # Convertir datos a strings para Redis
            email_data_str = {}
            for key, value in email_data.items():
                if isinstance(value, dict):
                    email_data_str[key] = json.dumps(value)
                else:
                    email_data_str[key] = str(value)
            
            message_id = await self.redis_service.xadd(
                self.email_stream,
                email_data_str
            )
            
            # También agregar a cola de prioridad alta
            await self.redis_service.zadd(
                self.email_queue,
                {message_id: datetime.now().timestamp()}
            )
            
            print(f"✅ Correo de confirmación enviado a Redis para {email}")
            print(f"   ID Mensaje: {message_id}")
            print(f"   Factura: {transaccion_data.get('numero_factura')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error enviando correo de confirmación: {e}")
            return False
    
    async def enviar_correo_cancelacion(
        self, 
        email: str, 
        transaccion_data: Dict[str, Any]
    ) -> bool:
        """
        Envía correo de cancelación de transacción
        
        Args:
            email: Email del usuario
            transaccion_data: Datos de la transacción cancelada
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            email_data = {
                "to": email,
                "subject": f"Cancelación de Compra - {transaccion_data.get('numero_factura', 'N/A')}",
                "template": "cancelacion_compra",
                "data": {
                    "transaccion_id": transaccion_data.get("transaccion_id"),
                    "numero_factura": transaccion_data.get("numero_factura"),
                    "fecha_cancelacion": datetime.now().isoformat(),
                    "motivo": transaccion_data.get("motivo", "Cancelación solicitada por el usuario"),
                    "reembolso": transaccion_data.get("reembolso", False)
                },
                "priority": "medium",
                "timestamp": datetime.now().isoformat()
            }
            
            # Convertir datos a strings para Redis
            email_data_str = {}
            for key, value in email_data.items():
                if isinstance(value, dict):
                    email_data_str[key] = json.dumps(value)
                else:
                    email_data_str[key] = str(value)
            
            message_id = await self.redis_service.xadd(
                self.email_stream,
                email_data_str
            )
            
            print(f"✅ Correo de cancelación enviado a Redis para {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando correo de cancelación: {e}")
            return False
    
    async def enviar_correo_recordatorio(
        self, 
        email: str, 
        funcion_data: Dict[str, Any]
    ) -> bool:
        """
        Envía correo de recordatorio de función
        
        Args:
            email: Email del usuario
            funcion_data: Datos de la función
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            email_data = {
                "to": email,
                "subject": f"Recordatorio - Función {funcion_data.get('pelicula_nombre', 'N/A')}",
                "template": "recordatorio_funcion",
                "data": {
                    "pelicula_nombre": funcion_data.get("pelicula_nombre"),
                    "fecha_funcion": funcion_data.get("fecha_funcion"),
                    "hora_funcion": funcion_data.get("hora_funcion"),
                    "sala": funcion_data.get("sala"),
                    "asientos": funcion_data.get("asientos", []),
                    "codigo_qr": funcion_data.get("codigo_qr", "")
                },
                "priority": "high",
                "timestamp": datetime.now().isoformat()
            }
            
            # Convertir datos a strings para Redis
            email_data_str = {}
            for key, value in email_data.items():
                if isinstance(value, dict):
                    email_data_str[key] = json.dumps(value)
                else:
                    email_data_str[key] = str(value)
            
            message_id = await self.redis_service.xadd(
                self.email_stream,
                email_data_str
            )
            
            print(f"✅ Correo de recordatorio enviado a Redis para {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando correo de recordatorio: {e}")
            return False
    
    async def procesar_cola_correos(self, batch_size: int = 10) -> int:
        """
        Procesa la cola de correos pendientes
        
        Args:
            batch_size: Número de correos a procesar por lote
            
        Returns:
            int: Número de correos procesados
        """
        try:
            # Obtener mensajes de la cola
            messages = await self.redis_service.xread(
                {self.email_stream: "0"},
                count=batch_size,
                block=1000  # 1 segundo de timeout
            )
            
            if not messages:
                return 0
            
            procesados = 0
            for stream, stream_messages in messages:
                for message_id, fields in stream_messages:
                    try:
                        # Convertir campos de vuelta a formato original
                        processed_fields = {}
                        for key, value in fields.items():
                            try:
                                # Intentar parsear como JSON si es un dict
                                if value.startswith('{') and value.endswith('}'):
                                    processed_fields[key] = json.loads(value)
                                else:
                                    processed_fields[key] = value
                            except:
                                processed_fields[key] = value
                        
                        # Verificar si usar envío real o simulado
                        # Usar envío real si las credenciales están configuradas correctamente
                        print(f"🔧 Verificando credenciales SMTP:")
                        print(f"   SMTP_USER: {settings.smtp_user}")
                        print(f"   SMTP_PASSWORD: {'***' if settings.smtp_password else 'None'}")
                        print(f"   ENVIRONMENT: {settings.environment}")
                        
                        if (settings.smtp_user and 
                            settings.smtp_user != "tu-email@gmail.com" and 
                            settings.smtp_password and 
                            settings.smtp_password != "tu-app-password-gmail"):
                            print("✅ Usando envío real de correo")
                            # Envío real
                            exito = await self._enviar_correo_real(processed_fields)
                        else:
                            print("⚠️  Usando simulación de correo")
                            # Simulación en desarrollo
                            exito = await self._simular_envio_correo(processed_fields)
                        
                        if exito:
                            # Marcar como procesado
                            await self.redis_service.xack(self.email_stream, "email_processor", message_id)
                            procesados += 1
                        else:
                            print(f"⚠️  Correo {message_id} no se pudo enviar, se reintentará")
                        
                    except Exception as e:
                        print(f"❌ Error procesando correo {message_id}: {e}")
            
            return procesados
            
        except Exception as e:
            print(f"❌ Error procesando cola de correos: {e}")
            return 0
    
    async def _simular_envio_correo(self, email_data: Dict[str, Any]) -> bool:
        """
        Simula el envío de un correo electrónico usando configuración de Docker
        
        Args:
            email_data: Datos del correo a enviar
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Verificar si las notificaciones de correo están habilitadas
            if not settings.enable_email_notifications:
                print(f"⚠️  Notificaciones de correo deshabilitadas para {email_data.get('to')}")
                return True
            
            # Simular delay de envío basado en configuración
            await asyncio.sleep(settings.email_retry_delay / 10)  # Reducido para simulación
            
            # Simular éxito/fallo (95% éxito)
            import random
            exito = random.random() < 0.95
            
            if exito:
                print(f"📧 Correo enviado exitosamente a {email_data.get('to')}")
                print(f"   Servidor SMTP: {settings.smtp_host}:{settings.smtp_port}")
                print(f"   Remitente: {settings.email_from_name} <{settings.email_from_address}>")
                print(f"   Asunto: {email_data.get('subject')}")
                print(f"   Template: {email_data.get('template')}")
                
                # Log de datos del correo
                if email_data.get("template") == "confirmacion_compra":
                    data = email_data.get("data", {})
                    print(f"   Factura: {data.get('numero_factura')}")
                    print(f"   Asientos: {data.get('asientos')}")
                    print(f"   Total: ${data.get('total', 0):,}")
                    print(f"   Método de pago: {data.get('metodo_pago', 'N/A')}")
                
                return True
            else:
                print(f"❌ Error simulado enviando correo a {email_data.get('to')}")
                print(f"   Servidor: {settings.smtp_host}")
                print(f"   Error: Timeout de conexión")
                return False
                
        except Exception as e:
            print(f"❌ Error en simulación de correo: {e}")
            return False
    
    async def obtener_estadisticas_correos(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de correos enviados
        
        Returns:
            Dict con estadísticas
        """
        try:
            # Contar mensajes en el stream
            total_messages = await self.redis_service.xlen(self.email_stream)
            
            # Contar correos por prioridad
            high_priority = await self.redis_service.zcount(
                self.email_queue, 
                datetime.now().timestamp() - 86400,  # Últimas 24 horas
                "+inf"
            )
            
            return {
                "total_correos_enviados": total_messages,
                "correos_prioridad_alta": high_priority,
                "fecha_ultima_actualizacion": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de correos: {e}")
            return {
                "total_correos_enviados": 0,
                "correos_prioridad_alta": 0,
                "error": str(e)
            }
    
    async def _enviar_correo_real(self, email_data: Dict[str, Any]) -> bool:
        """
        Envía un correo real usando SMTP con configuración de Docker
        
        Args:
            email_data: Datos del correo a enviar
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            print(f"📧 Iniciando envío real de correo a {email_data.get('to')}")
            print(f"   Servidor: {settings.smtp_host}:{settings.smtp_port}")
            print(f"   Usuario: {settings.smtp_user}")
            print(f"   TLS: {settings.smtp_use_tls}")
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = settings.smtp_user  # Usar exactamente el mismo formato que funcionó
            msg['To'] = email_data['to']
            msg['Subject'] = email_data['subject']
            msg['Reply-To'] = settings.email_reply_to
            
            # Crear contenido HTML del correo
            html_content = self._generar_template_html(email_data)
            msg.attach(MIMEText(html_content, 'html'))
            
            print(f"   Conectando a SMTP...")
            
            # Configurar conexión SMTP
            if settings.smtp_use_tls:
                server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
                print(f"   Iniciando TLS...")
                server.starttls()
            else:
                server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            
            print(f"   Autenticando...")
            # Autenticación
            server.login(settings.smtp_user, settings.smtp_password)
            
            print(f"   Enviando correo...")
            # Enviar correo
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Correo real enviado exitosamente a {email_data.get('to')}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando correo real: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            return False
    
    def _generar_template_html(self, email_data: Dict[str, Any]) -> str:
        """
        Genera contenido HTML para el correo basado en el template
        
        Args:
            email_data: Datos del correo
            
        Returns:
            str: Contenido HTML del correo
        """
        template = email_data.get("template", "default")
        data = email_data.get("data", {})
        
        if template == "confirmacion_compra":
            # Generar QR real
            codigo_qr = data.get('codigo_qr', 'QR-CODE')
            print(f"🔍 Debug QR - codigo_qr recibido: {codigo_qr}")
            qr_code_base64 = self._generar_qr_base64(codigo_qr)
            print(f"🔍 Debug QR - qr_code_base64 generado: {qr_code_base64[:50]}... (longitud: {len(qr_code_base64)})")
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Confirmación de Compra - Cinemax</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .header h1 {{ color: #e74c3c; margin: 0; }}
                    .details {{ margin: 20px 0; }}
                    .detail-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                    .total {{ font-size: 18px; font-weight: bold; color: #e74c3c; }}
                    .qr-code {{ text-align: center; margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }}
                    .qr-image {{ margin: 20px auto; display: block; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎬 Cinemax</h1>
                        <h2>¡Compra Confirmada!</h2>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <strong>Número de Factura:</strong>
                            <span>{data.get('numero_factura', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Asientos:</strong>
                            <span>{', '.join(data.get('asientos', []))}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Método de Pago:</strong>
                            <span>{data.get('metodo_pago', 'N/A')}</span>
                        </div>
                        <div class="detail-row total">
                            <strong>Total:</strong>
                            <span>${data.get('total', 0):,}</span>
                        </div>
                    </div>
                    
                    <div class="qr-code">
                        <h3>🎫 Código QR para Entrada</h3>
                        <img src="data:image/png;base64,{qr_code_base64}" alt="QR Code" class="qr-image" width="200" height="200">
                        <p><strong>{data.get('codigo_qr', 'QR-CODE')}</strong></p>
                        <p><small>Presenta este código en la entrada del cine</small></p>
                    </div>
                    
                    <div class="footer">
                        <p>Gracias por elegir Cinemax</p>
                        <p>Para soporte: {settings.email_reply_to}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        elif template == "cancelacion_compra":
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cancelación de Compra - Cinemax</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .header h1 {{ color: #e74c3c; margin: 0; }}
                    .details {{ margin: 20px 0; }}
                    .detail-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎬 Cinemax</h1>
                        <h2>Cancelación de Compra</h2>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <strong>Número de Factura:</strong>
                            <span>{data.get('numero_factura', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Motivo:</strong>
                            <span>{data.get('motivo', 'Cancelación solicitada')}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Reembolso:</strong>
                            <span>{'Sí' if data.get('reembolso') else 'No'}</span>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Para soporte: {settings.email_reply_to}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{email_data.get('subject', 'Notificación')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .header h1 {{ color: #e74c3c; margin: 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎬 Cinemax</h1>
                        <h2>{email_data.get('subject', 'Notificación')}</h2>
                    </div>
                    
                    <div class="footer">
                        <p>Para soporte: {settings.email_reply_to}</p>
                    </div>
                </div>
            </body>
            </html>
            """
    
    def _generar_qr_base64(self, codigo: str) -> str:
        """
        Genera un código QR y lo convierte a base64 para incluir en el HTML
        
        Args:
            codigo: Código a codificar en el QR
            
        Returns:
            str: Imagen QR en formato base64
        """
        try:
            import qrcode
            import base64
            from io import BytesIO
            
            # Crear QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(codigo)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = BytesIO()
            img.save(buffer, 'PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            print(f"❌ Error generando QR: {e}")
            # Retornar una imagen placeholder en base64 si falla
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    async def disconnect(self):
        """Desconectar del servicio de Redis"""
        await self.redis_service.disconnect()


# Instancia global del servicio de correo
email_service = EmailService() 