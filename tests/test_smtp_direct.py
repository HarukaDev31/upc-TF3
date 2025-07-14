#!/usr/bin/env python3
"""
Script de prueba directa de SMTP para verificar envío de correos
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def test_smtp_connection():
    """Prueba la conexión SMTP con las credenciales configuradas"""
    
    # Configuración SMTP (las mismas que vimos en el contenedor)
    smtp_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'user': 'harukakasugano31@gmail.com',
        'password': 'ebbimqokubqqnvqe',
        'use_tls': True,
        'verify_ssl': True,
        'timeout': 30,
        'max_retries': 3
    }
    
    print("=== PRUEBA DE CONEXIÓN SMTP ===")
    print(f"Host: {smtp_config['host']}")
    print(f"Puerto: {smtp_config['port']}")
    print(f"Usuario: {smtp_config['user']}")
    print(f"Contraseña: {smtp_config['password'][:10]}...")
    print(f"TLS: {smtp_config['use_tls']}")
    print(f"Verificar SSL: {smtp_config['verify_ssl']}")
    print()
    
    try:
        # Crear contexto SSL
        context = ssl.create_default_context()
        if not smtp_config['verify_ssl']:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        # Conectar al servidor SMTP
        print("Conectando al servidor SMTP...")
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=smtp_config['timeout'])
        
        # Iniciar TLS si está habilitado
        if smtp_config['use_tls']:
            print("Iniciando TLS...")
            server.starttls(context=context)
        
        # Autenticación
        print("Autenticando...")
        server.login(smtp_config['user'], smtp_config['password'])
        print("✅ Autenticación exitosa!")
        
        # Crear mensaje de prueba
        print("\nCreando mensaje de prueba...")
        msg = MIMEMultipart()
        msg['From'] = f"{smtp_config['user']}"  # Usar el mismo email como remitente
        msg['To'] = smtp_config['user']  # Enviar a sí mismo para prueba
        msg['Subject'] = 'Prueba de SMTP - Cinemax API'
        
        body = """
        <html>
        <body>
            <h2>Prueba de Envío de Correo</h2>
            <p>Este es un correo de prueba para verificar que el sistema SMTP funciona correctamente.</p>
            <p><strong>Configuración:</strong></p>
            <ul>
                <li>Host: smtp.gmail.com</li>
                <li>Puerto: 587</li>
                <li>TLS: Habilitado</li>
                <li>Usuario: harukakasugano31@gmail.com</li>
            </ul>
            <p>Si recibes este correo, significa que la configuración SMTP es correcta.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Enviar correo
        print("Enviando correo de prueba...")
        server.send_message(msg)
        print("✅ Correo enviado exitosamente!")
        
        # Cerrar conexión
        server.quit()
        print("✅ Conexión cerrada correctamente")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación: {e}")
        print("Verifica que las credenciales sean correctas y que la autenticación de 2 factores esté configurada correctamente.")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

async def test_email_service():
    """Prueba el servicio de correo de la aplicación"""
    
    print("\n=== PRUEBA DEL SERVICIO DE CORREO ===")
    
    # Configurar variables de entorno para la prueba
    os.environ['SMTP_HOST'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['SMTP_USER'] = 'harukakasugano31@gmail.com'
    os.environ['SMTP_PASSWORD'] = 'ebbimqokubqqnvqe'
    os.environ['SMTP_USE_TLS'] = 'true'
    os.environ['SMTP_VERIFY_SSL'] = 'true'
    os.environ['SMTP_TIMEOUT'] = '30'
    os.environ['SMTP_MAX_RETRIES'] = '3'
    
    try:
        from services.email_service import EmailService
        
        email_service = EmailService()
        await email_service.connect()
        
        # Datos de prueba
        test_data = {
            'cliente_email': 'harukakasugano31@gmail.com',
            'cliente_nombre': 'Usuario de Prueba',
            'funcion_id': 'test-123',
            'pelicula_titulo': 'Película de Prueba',
            'fecha_funcion': '2024-01-15 20:00',
            'asientos': ['A1', 'A2'],
            'total': 25.50,
            'transaccion_id': 'tx-test-123',
            'numero_factura': 'FAC-2024-001'
        }
        
        print("Enviando correo de confirmación de compra...")
        success = await email_service.enviar_correo_confirmacion_compra(
            email=test_data['cliente_email'],
            transaccion_data=test_data
        )
        
        if success:
            print("✅ Correo de confirmación enviado correctamente")
        else:
            print("❌ Error al enviar correo de confirmación")
            
        await email_service.disconnect()
        return success
        
    except Exception as e:
        print(f"❌ Error al probar el servicio de correo: {e}")
        return False

async def main():
    print("🚀 Iniciando pruebas de SMTP...\n")
    
    # Prueba directa de SMTP
    smtp_success = test_smtp_connection()
    
    if smtp_success:
        print("\n" + "="*50)
        print("✅ PRUEBA SMTP EXITOSA")
        print("="*50)
        
        # Prueba del servicio de correo
        service_success = await test_email_service()
        
        if service_success:
            print("\n" + "="*50)
            print("✅ TODAS LAS PRUEBAS EXITOSAS")
            print("El sistema de correo está funcionando correctamente")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("⚠️  SMTP funciona pero hay problemas en el servicio")
            print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ PRUEBA SMTP FALLIDA")
        print("Verifica las credenciales y configuración")
        print("="*50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 