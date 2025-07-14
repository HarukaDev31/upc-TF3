"""
Script de prueba para el servicio de correo con Redis
"""

import asyncio
import json
from datetime import datetime
from services.email_service import email_service


async def test_email_service():
    """Prueba el servicio de correo electrónico"""
    
    print("🚀 Iniciando prueba del servicio de correo electrónico...")
    
    try:
        # Conectar al servicio de correo
        await email_service.connect()
        print("✅ Conectado al servicio de correo")
        
        # Datos de prueba para una transacción
        transaccion_data = {
            "transaccion_id": "trans_123456789",
            "numero_factura": "CIN-20241201120000-ABC12345",
            "estado": "confirmado",
            "total": 45000,
            "asientos": ["A1", "A2", "B5"],
            "fecha_vencimiento": "2024-12-01T12:30:00",
            "resultado_pago": {
                "exitoso": True,
                "codigo_autorizacion": "AUTH17014320001234",
                "mensaje": "Pago procesado exitosamente"
            },
            "resumen": {
                "id": "trans_123456789",
                "numero_factura": "CIN-20241201120000-ABC12345",
                "fecha": "2024-12-01T12:00:00",
                "cliente_id": "user_123",
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
        email_usuario = "usuario@ejemplo.com"
        
        resultado_confirmacion = await email_service.enviar_correo_confirmacion_compra(
            email=email_usuario,
            transaccion_data=transaccion_data
        )
        
        if resultado_confirmacion:
            print("✅ Correo de confirmación enviado exitosamente")
        else:
            print("❌ Error enviando correo de confirmación")
        
        # 2. Enviar correo de cancelación
        print("\n📧 Enviando correo de cancelación...")
        transaccion_cancelada = {
            "transaccion_id": "trans_987654321",
            "numero_factura": "CIN-20241201130000-DEF67890",
            "motivo": "Cancelación solicitada por el usuario",
            "reembolso": True
        }
        
        resultado_cancelacion = await email_service.enviar_correo_cancelacion(
            email=email_usuario,
            transaccion_data=transaccion_cancelada
        )
        
        if resultado_cancelacion:
            print("✅ Correo de cancelación enviado exitosamente")
        else:
            print("❌ Error enviando correo de cancelación")
        
        # 3. Enviar correo de recordatorio
        print("\n📧 Enviando correo de recordatorio...")
        funcion_data = {
            "pelicula_nombre": "Avengers: Endgame",
            "fecha_funcion": "2024-12-15",
            "hora_funcion": "20:00",
            "sala": "Sala 1",
            "asientos": ["A1", "A2"],
            "codigo_qr": "QR123456"
        }
        
        resultado_recordatorio = await email_service.enviar_correo_recordatorio(
            email=email_usuario,
            funcion_data=funcion_data
        )
        
        if resultado_recordatorio:
            print("✅ Correo de recordatorio enviado exitosamente")
        else:
            print("❌ Error enviando correo de recordatorio")
        
        # 4. Procesar cola de correos
        print("\n🔄 Procesando cola de correos...")
        correos_procesados = await email_service.procesar_cola_correos(batch_size=5)
        print(f"✅ Se procesaron {correos_procesados} correos")
        
        # 5. Obtener estadísticas
        print("\n📊 Obteniendo estadísticas de correos...")
        estadisticas = await email_service.obtener_estadisticas_correos()
        print(f"📈 Estadísticas: {json.dumps(estadisticas, indent=2)}")
        
        # 6. Procesar más correos para demostrar el sistema
        print("\n🔄 Procesando más correos...")
        for i in range(3):
            correos_procesados = await email_service.procesar_cola_correos(batch_size=2)
            print(f"   Lote {i+1}: {correos_procesados} correos procesados")
            await asyncio.sleep(1)  # Simular delay entre lotes
        
        print("\n🎉 Prueba del servicio de correo completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        
    finally:
        # Desconectar del servicio
        await email_service.disconnect()
        print("🔌 Desconectado del servicio de correo")


async def test_multiple_transactions():
    """Prueba múltiples transacciones para simular carga"""
    
    print("\n🚀 Iniciando prueba de múltiples transacciones...")
    
    try:
        await email_service.connect()
        
        # Simular múltiples compras
        emails_usuarios = [
            "usuario1@ejemplo.com",
            "usuario2@ejemplo.com", 
            "usuario3@ejemplo.com",
            "usuario4@ejemplo.com",
            "usuario5@ejemplo.com"
        ]
        
        for i, email in enumerate(emails_usuarios):
            transaccion_data = {
                "transaccion_id": f"trans_{100000 + i}",
                "numero_factura": f"CIN-20241201{120000 + i}-ABC{i:05d}",
                "estado": "confirmado",
                "total": 25000 + (i * 5000),
                "asientos": [f"A{i+1}", f"B{i+1}"],
                "fecha_vencimiento": "2024-12-01T12:30:00",
                "resultado_pago": {
                    "exitoso": True,
                    "codigo_autorizacion": f"AUTH1701432000{i:04d}",
                    "mensaje": "Pago procesado exitosamente"
                },
                "resumen": {
                    "id": f"trans_{100000 + i}",
                    "numero_factura": f"CIN-20241201{120000 + i}-ABC{i:05d}",
                    "fecha": "2024-12-01T12:00:00",
                    "cliente_id": f"user_{i+1}",
                    "asientos": [
                        {"codigo": f"A{i+1}", "precio": 25000},
                        {"codigo": f"B{i+1}", "precio": 18000}
                    ],
                    "subtotal": 43000,
                    "descuentos": 0.05,
                    "impuestos": 8170,
                    "total": 25000 + (i * 5000),
                    "metodo_pago": "tarjeta_credito",
                    "estado": "confirmado"
                }
            }
            
            resultado = await email_service.enviar_correo_confirmacion_compra(
                email=email,
                transaccion_data=transaccion_data
            )
            
            if resultado:
                print(f"✅ Correo enviado a {email}")
            else:
                print(f"❌ Error enviando correo a {email}")
            
            await asyncio.sleep(0.2)  # Pequeño delay entre envíos
        
        # Procesar todos los correos
        print("\n🔄 Procesando todos los correos...")
        total_procesados = 0
        for i in range(5):
            procesados = await email_service.procesar_cola_correos(batch_size=3)
            total_procesados += procesados
            print(f"   Lote {i+1}: {procesados} correos procesados")
            await asyncio.sleep(0.5)
        
        print(f"📊 Total de correos procesados: {total_procesados}")
        
    except Exception as e:
        print(f"❌ Error en prueba de múltiples transacciones: {e}")
        
    finally:
        await email_service.disconnect()


if __name__ == "__main__":
    # Ejecutar pruebas
    asyncio.run(test_email_service())
    asyncio.run(test_multiple_transactions()) 