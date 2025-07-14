"""
Script para probar que los errores están solucionados
"""

import asyncio
import json
from datetime import datetime
from services.email_service import email_service
from config.settings import settings


async def test_email_service_fixed():
    """Prueba el servicio de correo con las correcciones"""
    
    print("🔧 Probando servicio de correo con correcciones...")
    
    try:
        # Conectar al servicio
        await email_service.connect()
        print("✅ Conexión establecida")
        
        # Datos de prueba
        transaccion_data = {
            "transaccion_id": "test_fix_001",
            "numero_factura": "CIN-FIX-123",
            "estado": "confirmado",
            "total": 30000,
            "asientos": ["A1", "B2"],
            "fecha_vencimiento": "2024-12-01T12:30:00",
            "resultado_pago": {
                "exitoso": True,
                "codigo_autorizacion": "AUTH-FIX-123"
            },
            "resumen": {
                "id": "test_fix_001",
                "numero_factura": "CIN-FIX-123",
                "metodo_pago": "tarjeta_credito",
                "total": 30000
            }
        }
        
        # Probar envío de correo
        print("\n📧 Probando envío de correo...")
        resultado = await email_service.enviar_correo_confirmacion_compra(
            email="test@ejemplo.com",
            transaccion_data=transaccion_data
        )
        
        if resultado:
            print("✅ Correo enviado exitosamente")
        else:
            print("❌ Error enviando correo")
        
        # Probar procesamiento
        print("\n🔄 Probando procesamiento...")
        procesados = await email_service.procesar_cola_correos(batch_size=5)
        print(f"✅ Procesados {procesados} correos")
        
        # Probar estadísticas
        print("\n📊 Probando estadísticas...")
        stats = await email_service.obtener_estadisticas_correos()
        print(f"📈 Estadísticas: {json.dumps(stats, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False
        
    finally:
        await email_service.disconnect()


async def test_redis_methods():
    """Prueba los métodos de Redis que estaban faltando"""
    
    print("\n🔗 Probando métodos de Redis...")
    
    try:
        await email_service.connect()
        
        # Probar método liberar_asiento
        resultado = await email_service.redis_service.liberar_asiento(
            funcion_id="fun_001",
            asiento="A1",
            usuario_id="user_123"
        )
        
        print(f"✅ liberar_asiento: {resultado}")
        
        # Probar operaciones básicas
        await email_service.redis_service.set("test_fix", "value_fix")
        value = await email_service.redis_service.get("test_fix")
        print(f"✅ Operación básica: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando Redis: {e}")
        return False
        
    finally:
        await email_service.disconnect()


async def test_error_handling():
    """Prueba el manejo de errores"""
    
    print("\n🛡️  Probando manejo de errores...")
    
    try:
        # Probar con Redis no disponible
        email_service.redis_service.redis_client = None
        
        resultado = await email_service.enviar_correo_confirmacion_compra(
            email="test@ejemplo.com",
            transaccion_data={
                "transaccion_id": "test_error_001",
                "numero_factura": "CIN-ERROR-123",
                "estado": "confirmado",
                "total": 25000,
                "asientos": ["A1"],
                "resumen": {
                    "metodo_pago": "efectivo",
                    "total": 25000
                }
            }
        )
        
        if resultado:
            print("✅ Manejo de errores funcionando (envío directo)")
        else:
            print("❌ Error en manejo de errores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en manejo de errores: {e}")
        return False


async def main():
    """Función principal"""
    
    print("🚀 Iniciando pruebas de correcciones...")
    
    # 1. Probar servicio de correo
    await test_email_service_fixed()
    
    # 2. Probar métodos de Redis
    await test_redis_methods()
    
    # 3. Probar manejo de errores
    await test_error_handling()
    
    print("\n🎉 Pruebas de correcciones completadas!")


if __name__ == "__main__":
    asyncio.run(main()) 