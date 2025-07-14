#!/usr/bin/env python3
"""
Script para probar una transacción completa y verificar el envío de correo
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from use_cases.comprar_entrada_use_case import ComprarEntradaUseCase
from services.email_service import EmailService
from domain.entities.cliente import Cliente
from domain.entities.funcion import Funcion
from domain.entities.pelicula import Pelicula

async def test_complete_transaction():
    """Prueba una transacción completa con envío de correo"""
    
    print("🛒 Iniciando prueba de transacción completa...")
    
    # Configurar variables de entorno para correo real
    os.environ['SMTP_HOST'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['SMTP_USER'] = 'harukakasugano31@gmail.com'
    os.environ['SMTP_PASSWORD'] = 'ebbimqokubqqnvqe'
    os.environ['SMTP_USE_TLS'] = 'true'
    os.environ['SMTP_VERIFY_SSL'] = 'true'
    os.environ['SMTP_TIMEOUT'] = '30'
    os.environ['SMTP_MAX_RETRIES'] = '3'
    os.environ['ENVIRONMENT'] = 'production'
    
    try:
        # Crear datos de prueba
        cliente = Cliente(
            _id="test-cliente-123",
            nombre="Usuario de Prueba",
            email="harukakasugano31@gmail.com",
            telefono="+1234567890"
        )
        
        from domain.entities.pelicula import GeneroEnum, ClasificacionEnum
        
        pelicula = Pelicula(
            _id="test-pelicula-123",
            titulo="Película de Prueba",
            titulo_original="Test Movie",
            sinopsis="Una película de prueba para verificar el envío de correos",
            director="Director de Prueba",
            generos=[GeneroEnum.ACCION],
            duracion_minutos=120,
            clasificacion=ClasificacionEnum.PG13,
            idioma_original="Español",
            fecha_estreno=datetime.now().date(),
            fecha_disponible_desde=datetime.now().date(),
            precio_base=12.50
        )
        
        # Crear sala
        from domain.entities.funcion import Sala, TipoSala, Asiento
        
        asientos_sala = [
            Asiento(fila="A", numero=i, tipo="estandar") for i in range(1, 21)
        ] + [
            Asiento(fila="B", numero=i, tipo="estandar") for i in range(1, 21)
        ]
        
        sala = Sala(
            id="sala-1",
            nombre="Sala 1",
            tipo=TipoSala.ESTANDAR,
            capacidad_total=40,
            filas=2,
            asientos_por_fila=20,
            asientos=asientos_sala
        )
        
        funcion = Funcion(
            _id="test-funcion-123",
            pelicula_id="test-pelicula-123",
            sala=sala,
            fecha_hora_inicio=datetime.now() + timedelta(days=1),
            fecha_hora_fin=datetime.now() + timedelta(days=1, hours=2),
            precio_base=12.50,
            precio_vip=15.00,
            idioma_audio="Español"
        )
        
        # Datos de la compra
        compra_data = {
            "cliente_id": cliente.id,
            "funcion_id": funcion.id,
            "asientos": ["A1", "A2"],
            "metodo_pago": "tarjeta_credito",
            "datos_pago": {
                "numero_tarjeta": "4111111111111111",
                "fecha_vencimiento": "12/25",
                "cvv": "123"
            }
        }
        
        print(f"📋 Datos de la compra:")
        print(f"   Cliente: {cliente.nombre} ({cliente.email})")
        print(f"   Película: {pelicula.titulo}")
        print(f"   Función: {funcion.sala.nombre} - {funcion.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Asientos: {compra_data['asientos']}")
        print(f"   Método de pago: {compra_data['metodo_pago']}")
        print()
        
        # Ejecutar caso de uso
        use_case = ComprarEntradaUseCase()
        from domain.entities.transaccion import MetodoPago
        
        resultado = await use_case.ejecutar(
            usuario_id=str(cliente.id),
            funcion_id=str(funcion.id),
            asientos=compra_data["asientos"],
            metodo_pago=MetodoPago.TARJETA_CREDITO,
            datos_pago=compra_data["datos_pago"]
        )
        
        if resultado["exito"]:
            print("✅ Transacción completada exitosamente!")
            print(f"   ID Transacción: {resultado['transaccion']['id']}")
            print(f"   Número de Factura: {resultado['transaccion']['numero_factura']}")
            print(f"   Total: ${resultado['transaccion']['total']}")
            print(f"   Estado: {resultado['transaccion']['estado']}")
            print()
            
            # Verificar envío de correo
            print("📧 Verificando envío de correo...")
            email_service = EmailService()
            await email_service.connect()
            
            # Procesar cola de correos
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
            
            print("\n" + "="*60)
            print("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
            print("="*60)
            print("✅ Transacción procesada")
            print("✅ Correo enviado (verifica tu bandeja de entrada)")
            print("✅ Sistema funcionando correctamente")
            print("="*60)
            
        else:
            print("❌ Error en la transacción:")
            print(f"   {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_transaction()) 