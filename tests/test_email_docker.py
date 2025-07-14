"""
Script de prueba para el servicio de correo con configuración de Docker
"""

import asyncio
import json
from datetime import datetime
from services.email_service import email_service
from config.settings import settings


async def test_email_with_docker_config():
    """Prueba el servicio de correo con configuración de Docker"""
    
    print("🚀 Iniciando prueba del servicio de correo con configuración Docker...")
    print(f"📧 Configuración SMTP: {settings.smtp_host}:{settings.smtp_port}")
    print(f"👤 Usuario SMTP: {settings.smtp_user}")
    print(f"🔧 Entorno: {settings.environment}")
    print(f"📬 Notificaciones habilitadas: {settings.enable_email_notifications}")
    
    try:
        # Conectar al servicio de correo
        await email_service.connect()
        print("✅ Conectado al servicio de correo")
        
        # Datos de prueba para una transacción
        transaccion_data = {
            "transaccion_id": "trans_docker_001",
            "numero_factura": "CIN-20241201120000-DOCKER123",
            "estado": "confirmado",
            "total": 45000,
            "asientos": ["A1", "A2", "B5"],
            "fecha_vencimiento": "2024-12-01T12:30:00",
            "resultado_pago": {
                "exitoso": True,
                "codigo_autorizacion": "AUTH1701432000DOCKER",
                "mensaje": "Pago procesado exitosamente"
            },
            "resumen": {
                "id": "trans_docker_001",
                "numero_factura": "CIN-20241201120000-DOCKER123",
                "fecha": "2024-12-01T12:00:00",
                "cliente_id": "user_docker",
                "asientos": [
                    {"codigo": "A1", "precio": 25000},
                    {"codigo": "A2", "precio": 25000},
                    {"codigo": "B5", "precio": 18000}
                ],
                "subtotal": 68000,
                "descuentos": 0.1,
                "impuestos": 12240,
                "total": 45000,
                "metodo_pago": "tarjeta_credito",
                "estado": "confirmado"
            }
        }
        
        # 1. Enviar correo de confirmación de compra
        print("\n📧 Enviando correo de confirmación de compra...")
        email_usuario = "test@ejemplo.com"
        
        resultado_confirmacion = await email_service.enviar_correo_confirmacion_compra(
            email=email_usuario,
            transaccion_data=transaccion_data
        )
        
        if resultado_confirmacion:
            print("✅ Correo de confirmación enviado exitosamente")
        else:
            print("❌ Error enviando correo de confirmación")
        
        # 2. Procesar cola de correos
        print("\n🔄 Procesando cola de correos...")
        correos_procesados = await email_service.procesar_cola_correos(batch_size=5)
        print(f"✅ Se procesaron {correos_procesados} correos")
        
        # 3. Obtener estadísticas
        print("\n📊 Obteniendo estadísticas de correos...")
        estadisticas = await email_service.obtener_estadisticas_correos()
        print(f"📈 Estadísticas: {json.dumps(estadisticas, indent=2)}")
        
        # 4. Verificar configuración
        print("\n🔧 Verificando configuración...")
        print(f"   SMTP Host: {settings.smtp_host}")
        print(f"   SMTP Port: {settings.smtp_port}")
        print(f"   SMTP User: {settings.smtp_user}")
        print(f"   SMTP TLS: {settings.smtp_use_tls}")
        print(f"   From Name: {settings.email_from_name}")
        print(f"   From Address: {settings.email_from_address}")
        print(f"   Reply To: {settings.email_reply_to}")
        print(f"   Batch Size: {settings.email_batch_size}")
        print(f"   Retry Delay: {settings.email_retry_delay}")
        
        print("\n🎉 Prueba del servicio de correo con Docker completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        
    finally:
        # Desconectar del servicio
        await email_service.disconnect()
        print("🔌 Desconectado del servicio de correo")


async def test_email_templates():
    """Prueba los templates de correo HTML"""
    
    print("\n🎨 Probando templates de correo HTML...")
    
    try:
        await email_service.connect()
        
        # Probar template de confirmación
        email_data = {
            "to": "test@ejemplo.com",
            "subject": "Confirmación de Compra - Test Docker",
            "template": "confirmacion_compra",
            "data": {
                "transaccion_id": "trans_test_001",
                "numero_factura": "CIN-20241201120000-TEST123",
                "asientos": ["A1", "A2", "B5"],
                "total": 45000,
                "metodo_pago": "tarjeta_credito",
                "codigo_qr": "QR-TEST-123"
            }
        }
        
        # Generar HTML del template
        html_content = email_service._generar_template_html(email_data)
        
        print("✅ Template de confirmación generado:")
        print(f"   Longitud HTML: {len(html_content)} caracteres")
        print(f"   Incluye Cinemax: {'Cinemax' in html_content}")
        print(f"   Incluye código QR: {'QR-TEST-123' in html_content}")
        
        # Probar template de cancelación
        email_data_cancel = {
            "to": "test@ejemplo.com",
            "subject": "Cancelación de Compra - Test Docker",
            "template": "cancelacion_compra",
            "data": {
                "transaccion_id": "trans_test_002",
                "numero_factura": "CIN-20241201130000-CANCEL123",
                "motivo": "Cancelación de prueba",
                "reembolso": True
            }
        }
        
        html_cancel = email_service._generar_template_html(email_data_cancel)
        
        print("✅ Template de cancelación generado:")
        print(f"   Longitud HTML: {len(html_cancel)} caracteres")
        print(f"   Incluye motivo: {'Cancelación de prueba' in html_cancel}")
        print(f"   Incluye reembolso: {'Sí' in html_cancel}")
        
    except Exception as e:
        print(f"❌ Error probando templates: {e}")
        
    finally:
        await email_service.disconnect()


async def test_email_configuration():
    """Prueba la configuración de correo"""
    
    print("\n⚙️  Probando configuración de correo...")
    
    # Verificar configuración
    config_ok = True
    
    if not settings.smtp_host:
        print("❌ SMTP_HOST no configurado")
        config_ok = False
    
    if not settings.smtp_user:
        print("❌ SMTP_USER no configurado")
        config_ok = False
    
    if settings.smtp_user == "tu-email@gmail.com":
        print("⚠️  SMTP_USER usa valor por defecto")
    
    if settings.smtp_password == "tu-app-password-gmail":
        print("⚠️  SMTP_PASSWORD usa valor por defecto")
    
    if settings.environment == "development":
        print("ℹ️  Ejecutando en modo desarrollo (simulación)")
    else:
        print("ℹ️  Ejecutando en modo producción (envío real)")
    
    if settings.enable_email_notifications:
        print("✅ Notificaciones de correo habilitadas")
    else:
        print("❌ Notificaciones de correo deshabilitadas")
    
    if config_ok:
        print("✅ Configuración de correo válida")
    else:
        print("❌ Configuración de correo incompleta")


if __name__ == "__main__":
    # Ejecutar pruebas
    asyncio.run(test_email_configuration())
    asyncio.run(test_email_templates())
    asyncio.run(test_email_with_docker_config()) 