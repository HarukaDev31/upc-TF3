#!/usr/bin/env python3
"""
Script para probar los endpoints de la API
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"
ENDPOINTS = [
    "/",
    "/health", 
    "/test",
    "/api/v1/peliculas",
    "/api/v1/funciones/fun_001/asientos"
]

def test_endpoint(url, name):
    """Prueba un endpoint específico"""
    try:
        print(f"\n🔍 Probando {name}: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta JSON válida:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"⚠️  Respuesta no es JSON válido:")
                print(f"📄 Contenido: {response.text}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Contenido: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a {url}")
        print("💡 Asegúrate de que la aplicación esté corriendo en http://localhost:8000")
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout al conectar a {url}")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de endpoints...")
    print(f"🎯 URL base: {BASE_URL}")
    
    # Esperar un poco para que la aplicación se inicie
    print("⏳ Esperando 3 segundos para que la aplicación se inicie...")
    time.sleep(3)
    
    # Probar cada endpoint
    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        test_endpoint(url, endpoint)
    
    print("\n🎉 Pruebas completadas!")
    print("📖 Para ver la documentación automática, visita: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 