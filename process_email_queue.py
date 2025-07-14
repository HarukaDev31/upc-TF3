#!/usr/bin/env python3
"""
Script para procesar la cola de correos desde Redis
"""

import asyncio
import os
from services.email_service import EmailService

async def process_email_queue():
    """Procesa la cola de correos desde Redis"""
    
    print("📧 Procesando cola de correos...")
    
    # Configurar variables de entorno directamente
    os.environ['SMTP_HOST'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['SMTP_USER'] = 'harukakasugano31@gmail.com'
    os.environ['SMTP_PASSWORD'] = 'ebbimqokubqqnvqe'
    os.environ['SMTP_USE_TLS'] = 'true'
    os.environ['SMTP_VERIFY_SSL'] = 'true'
    os.environ['SMTP_TIMEOUT'] = '30'
    os.environ['SMTP_MAX_RETRIES'] = '3'
    os.environ['ENVIRONMENT'] = 'production'  # Cambiar a production para enviar correos reales
    
    try:
        email_service = EmailService()
        await email_service.connect()
        
        print("✅ Conectado al servicio de correo")
        
        # Procesar correos en lotes
        processed_count = await email_service.procesar_cola_correos(batch_size=5)
        
        print(f"✅ Procesados {processed_count} correos")
        
        # Obtener estadísticas
        stats = await email_service.obtener_estadisticas_correos()
        print("\n📊 Estadísticas de correos:")
        print(f"   Total enviados: {stats.get('total_enviados', 0)}")
        print(f"   Enviados hoy: {stats.get('enviados_hoy', 0)}")
        print(f"   Pendientes: {stats.get('pendientes', 0)}")
        print(f"   Errores: {stats.get('errores', 0)}")
        
        await email_service.disconnect()
        
    except Exception as e:
        print(f"❌ Error procesando cola de correos: {e}")

if __name__ == "__main__":
    asyncio.run(process_email_queue()) 