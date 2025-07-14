#!/usr/bin/env python3
"""
Script para probar envío de correo con HTML similar al de la aplicación
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_html_email():
    """Prueba envío de correo con HTML similar al de la aplicación"""
    
    print("📧 Probando envío de correo con HTML...")
    
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
        
        # Crear mensaje con HTML similar al de la aplicación
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        msg['Subject'] = 'Test HTML Email - Cinemax API'
        
        # HTML similar al de la aplicación
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Confirmación de Compra - Cinemax</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #e74c3c; margin: 0; }
                .details { margin: 20px 0; }
                .detail-row { display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
                .total { font-size: 18px; font-weight: bold; color: #e74c3c; }
                .qr-code { text-align: center; margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
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
                        <span>TEST-2024-001</span>
                    </div>
                    <div class="detail-row">
                        <strong>Asientos:</strong>
                        <span>D3</span>
                    </div>
                    <div class="detail-row">
                        <strong>Método de Pago:</strong>
                        <span>Tarjeta de Crédito</span>
                    </div>
                    <div class="detail-row total">
                        <strong>Total:</strong>
                        <span>$21,420</span>
                    </div>
                </div>
                
                <div class="qr-code">
                    <h3>🎫 Código QR para Entrada</h3>
                    <p><strong>QR-TEST-123</strong></p>
                    <p><small>Presenta este código en la entrada del cine</small></p>
                </div>
                
                <div class="footer">
                    <p>Gracias por elegir Cinemax</p>
                    <p>Para soporte: support@cinemax.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        print("Enviando mensaje HTML...")
        server.send_message(msg)
        print("✅ Mensaje HTML enviado exitosamente!")
        
        server.quit()
        print("✅ Conexión cerrada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_html_email() 