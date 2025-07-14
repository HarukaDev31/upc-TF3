"""
Script para probar las credenciales SMTP directamente
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings


def test_smtp_connection():
    """Prueba la conexión SMTP directamente"""
    
    print("🔧 Probando conexión SMTP...")
    print(f"   Host: {settings.smtp_host}")
    print(f"   Port: {settings.smtp_port}")
    print(f"   User: {settings.smtp_user}")
    print(f"   Password: {'***' if settings.smtp_password else 'None'}")
    print(f"   TLS: {settings.smtp_use_tls}")
    print(f"   From: {settings.email_from_address}")
    
    try:
        # Crear mensaje de prueba
        msg = MIMEMultipart()
        msg['From'] = f"{settings.email_from_name} <{settings.email_from_address}>"
        msg['To'] = "harukakasugano31@gmail.com"
        msg['Subject'] = "Prueba de Conexión SMTP - Cinemax"
        msg['Reply-To'] = settings.email_reply_to
        
        # Contenido simple
        html_content = """
        <html>
        <body>
            <h1>🎬 Prueba de Conexión SMTP</h1>
            <p>Este es un correo de prueba para verificar que la configuración SMTP funciona correctamente.</p>
            <p><strong>Servidor:</strong> {}</p>
            <p><strong>Usuario:</strong> {}</p>
            <p><strong>TLS:</strong> {}</p>
        </body>
        </html>
        """.format(settings.smtp_host, settings.smtp_user, settings.smtp_use_tls)
        
        msg.attach(MIMEText(html_content, 'html'))
        
        print("\n📧 Conectando a SMTP...")
        
        # Conectar a SMTP
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            print("   Iniciando TLS...")
            server.starttls()
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        
        print("   Autenticando...")
        server.login(settings.smtp_user, settings.smtp_password)
        
        print("   Enviando correo de prueba...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Correo de prueba enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión SMTP: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False


def test_settings():
    """Prueba la configuración de settings"""
    
    print("\n⚙️  Verificando configuración...")
    
    # Verificar variables críticas
    variables = {
        "SMTP_HOST": settings.smtp_host,
        "SMTP_PORT": settings.smtp_port,
        "SMTP_USER": settings.smtp_user,
        "SMTP_PASSWORD": settings.smtp_password,
        "SMTP_USE_TLS": settings.smtp_use_tls,
        "EMAIL_FROM_NAME": settings.email_from_name,
        "EMAIL_FROM_ADDRESS": settings.email_from_address,
        "EMAIL_REPLY_TO": settings.email_reply_to,
        "ENVIRONMENT": settings.environment
    }
    
    for var_name, value in variables.items():
        if value is None or value == "":
            print(f"❌ {var_name}: None/Empty")
        elif "tu-" in str(value):
            print(f"⚠️  {var_name}: {value} (valor por defecto)")
        else:
            print(f"✅ {var_name}: {value}")


if __name__ == "__main__":
    test_settings()
    test_smtp_connection() 