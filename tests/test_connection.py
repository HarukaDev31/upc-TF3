#!/usr/bin/env python3
"""
Script simple para probar la conexión a la API
"""

import requests
import time

def test_api():
    """Prueba la conexión a la API"""
    print("🔍 Probando conexión a la API...")
    
    # Esperar un poco para que la aplicación se inicie
    print("⏳ Esperando 5 segundos...")
    time.sleep(5)
    
    try:
        # Probar el endpoint raíz
        print("🌐 Probando http://localhost:8000/")
        response = requests.get("http://localhost:8000/", timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            print("✅ Conexión exitosa!")
            print(f"📄 Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Contenido: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a http://localhost:8000/")
        print("💡 Verifica que:")
        print("   1. La aplicación esté corriendo")
        print("   2. El puerto 8000 esté disponible")
        print("   3. No haya otro servicio usando el puerto")
    except requests.exceptions.Timeout:
        print("⏰ Timeout al conectar")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")

def check_port():
    """Verifica si el puerto 8000 está en uso"""
    import socket
    
    print("🔍 Verificando puerto 8000...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Puerto 8000 está en uso (probablemente la API)")
        else:
            print("❌ Puerto 8000 no está en uso")
            print("💡 La aplicación no está corriendo")
            
    except Exception as e:
        print(f"💥 Error al verificar puerto: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de conexión...")
    
    # Verificar puerto
    check_port()
    
    # Probar API
    test_api()
    
    print("\n🎉 Diagnóstico completado!") 