"""
Script de prueba simplificado para Redis y correo
"""

import asyncio
import json
from datetime import datetime
from services.email_service import email_service
from config.settings import settings


async def test_redis_connection():
    """Prueba la conexión a Redis"""
    
    print("🔗 Probando conexión a Redis...")
    
    try:
        await email_service.connect()
        print("✅ Conexión a Redis exitosa")
        
        # Probar operación básica
        await email_service.redis_service.set("test_key", "test_value")
        value = await email_service.redis_service.get("test_key")
        print(f"✅ Test Redis: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return False


async def test_email_send():
    """Prueba el envío de correo"""
    
    print("\n📧 Probando envío de correo...")
    
    try:
        # Datos de prueba simples
        transaccion_data = {
            "transaccion_id": "test_001",
            "numero_factura": "CIN-TEST-123",
            "estado": "confirmado",
            "total": 25000,
            "asientos": ["A1"],
            "fecha_vencimiento": "2024-12-01T12:30:00",
            "resultado_pago": {
                "exitoso": True,
                "codigo_autorizacion": "AUTH123"
            },
            "resumen": {
                "id": "test_001",
                "numero_factura": "CIN-TEST-123",
                "metodo_pago": "efectivo",
                "total": 25000
            }
        }
        
        # Enviar correo
        resultado = await email_service.enviar_correo_confirmacion_compra(
            email="test@ejemplo.com",
            transaccion_data=transaccion_data
        )
        
        if resultado:
            print("✅ Correo enviado a Redis exitosamente")
        else:
            print("❌ Error enviando correo")
            
        return resultado
        
    except Exception as e:
        print(f"❌ Error en envío de correo: {e}")
        return False


async def test_email_processing():
    """Prueba el procesamiento de correos"""
    
    print("\n🔄 Probando procesamiento de correos...")
    
    try:
        # Procesar cola
        procesados = await email_service.procesar_cola_correos(batch_size=5)
        print(f"✅ Procesados {procesados} correos")
        
        # Obtener estadísticas
        stats = await email_service.obtener_estadisticas_correos()
        print(f"📊 Estadísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando correos: {e}")
        return False


async def test_simple_redis_stream():
    """Prueba simple de Redis Stream"""
    
    print("\n📡 Probando Redis Stream...")
    
    try:
        # Agregar mensaje simple
        test_data = {
            "to": "test@ejemplo.com",
            "subject": "Test Simple",
            "message": "Este es un mensaje de prueba"
        }
        
        # Convertir a strings
        redis_data = {}
        for key, value in test_data.items():
            redis_data[key] = str(value)
        
        message_id = await email_service.redis_service.xadd(
            "test_stream",
            redis_data
        )
        
        print(f"✅ Mensaje agregado: {message_id}")
        
        # Leer mensaje
        messages = await email_service.redis_service.xread(
            {"test_stream": "0"},
            count=1
        )
        
        if messages:
            print(f"✅ Mensaje leído: {messages}")
        else:
            print("❌ No se pudo leer mensaje")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en Redis Stream: {e}")
        return False


async def main():
    """Función principal de prueba"""
    
    print("🚀 Iniciando pruebas de Redis y Correo...")
    
    # 1. Probar conexión Redis
    redis_ok = await test_redis_connection()
    
    if not redis_ok:
        print("❌ No se puede continuar sin Redis")
        return
    
    # 2. Probar Redis Stream
    await test_simple_redis_stream()
    
    # 3. Probar envío de correo
    email_ok = await test_email_send()
    
    # 4. Probar procesamiento
    if email_ok:
        await test_email_processing()
    
    # 5. Limpiar
    await email_service.disconnect()
    print("\n🎉 Pruebas completadas!")


if __name__ == "__main__":
    asyncio.run(main()) 