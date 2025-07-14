#!/usr/bin/env python3
"""
Script para probar específicamente la autenticación de Gmail
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_auth():
    """Prueba específicamente la autenticación de Gmail"""
    
    print("🔐 Probando autenticación de Gmail...")
    
    # Configuración SMTP
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "harukakasugano31@gmail.com"
    smtp_password = "ebbimqokubqqnvqe"
    
    try:
        # Crear contexto SSL
        context = ssl.create_default_context()
        
        print(f"Conectando a {smtp_host}:{smtp_port}...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        
        print("Iniciando TLS...")
        server.starttls(context=context)
        
        print(f"Autenticando con {smtp_user}...")
        server.login(smtp_user, smtp_password)
        print("✅ Autenticación exitosa!")
        
        # Crear mensaje de prueba simple
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        msg['Subject'] = 'Test Gmail Auth - ' + str(datetime.now())
        
        body = "Este es un test de autenticación de Gmail."
        msg.attach(MIMEText(body, 'plain'))
        
        print("Enviando mensaje de prueba...")
        server.send_message(msg)
        print("✅ Mensaje enviado exitosamente!")
        
        server.quit()
        print("✅ Conexión cerrada correctamente")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que la contraseña de aplicación sea correcta")
        print("2. Ve a https://myaccount.google.com/apppasswords")
        print("3. Genera una nueva contraseña de aplicación")
        print("4. Asegúrate de que la autenticación de 2 factores esté habilitada")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    test_gmail_auth() 