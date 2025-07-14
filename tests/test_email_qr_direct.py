#!/usr/bin/env python3
"""
Script de prueba directo para verificar el flujo completo de QR en email
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.email_service import email_service

async def test_email_qr():
    """Prueba directa del envío de email con QR"""
    
    # Datos de prueba
    transaccion_data = {
        "transaccion_id": "test-12345",
        "numero_factura": "CIN-TEST-001",
        "estado": "confirmado",
        "total": 25000,
        "asientos": ["A1", "A2"],
        "fecha_vencimiento": "2025-01-15T20:00:00",
        "resultado_pago": {"exitoso": True},
        "resumen": {"metodo_pago": "tarjeta"},
        "codigo_qr": "test-uuid-12345-67890"  # UUID de prueba
    }
    
    print("🧪 Probando envío de email con QR...")
    print(f"📧 Datos de transacción: {transaccion_data}")
    
    try:
        # Conectar al servicio de email
        await email_service.connect()
        
        # Forzar envío directo (sin Redis)
        email_service.redis_service.redis_client = None
        
        # Enviar correo de prueba
        resultado = await email_service.enviar_correo_confirmacion_compra(
            email="harukakasugano31@gmail.com",
            transaccion_data=transaccion_data
        )
        
        if resultado:
            print("✅ Email enviado correctamente")
        else:
            print("❌ Error enviando email")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_qr()) 