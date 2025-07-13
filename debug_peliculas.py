#!/usr/bin/env python3
"""
Script para diagnosticar el problema con el endpoint de películas
"""

import requests
import json
import time

def test_peliculas_endpoint():
    """Prueba específicamente el endpoint de películas"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/test",
        "/api/v1/peliculas-minimal",
        "/api/v1/peliculas-simple", 
        "/api/v1/peliculas"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n{'='*50}")
        print(f"🔍 Probando: {endpoint}")
        print(f"🌐 URL: {url}")
        print(f"{'='*50}")
        
        try:
            # Hacer la petición con timeout
            response = requests.get(url, timeout=15)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Content-Type: {response.headers.get('content-type', 'No especificado')}")
            print(f"📏 Content-Length: {response.headers.get('content-length', 'No especificado')}")
            
            # Mostrar todos los headers
            print(f"📋 Todos los headers:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")
            
            # Analizar el contenido
            if response.status_code == 200:
                if response.content:
                    print(f"📄 Contenido (bytes): {len(response.content)} bytes")
                    print(f"📄 Contenido (texto): {response.text[:200]}...")
                    
                    try:
                        data = response.json()
                        print(f"✅ JSON válido:")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError as e:
                        print(f"❌ Error al parsear JSON: {e}")
                        print(f"📄 Contenido completo: {response.text}")
                else:
                    print("❌ Respuesta vacía (sin contenido)")
            else:
                print(f"❌ Error HTTP {response.status_code}")
                print(f"📄 Contenido de error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ No se pudo conectar a {url}")
            print("💡 Asegúrate de que la aplicación esté corriendo")
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout al conectar a {url}")
        except Exception as e:
            print(f"💥 Error inesperado: {e}")

def test_with_curl_equivalent():
    """Simula lo que haría curl"""
    import subprocess
    import sys
    
    print(f"\n{'='*50}")
    print("🔧 Probando con equivalente a curl")
    print(f"{'='*50}")
    
    try:
        # Usar Python para simular curl
        import urllib.request
        import urllib.error
        
        url = "http://localhost:8000/api/v1/peliculas"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"📊 Status Code: {response.status}")
            print(f"📋 Headers:")
            for header, value in response.getheaders():
                print(f"   {header}: {value}")
            
            content = response.read()
            print(f"📄 Contenido (bytes): {len(content)}")
            print(f"📄 Contenido (texto): {content.decode('utf-8')[:200]}...")
            
    except urllib.error.URLError as e:
        print(f"❌ Error de URL: {e}")
    except Exception as e:
        print(f"💥 Error: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando diagnóstico del endpoint de películas...")
    
    # Esperar un poco
    print("⏳ Esperando 2 segundos...")
    time.sleep(2)
    
    # Probar con requests
    test_peliculas_endpoint()
    
    # Probar con urllib (equivalente a curl)
    test_with_curl_equivalent()
    
    print(f"\n{'='*50}")
    print("🎉 Diagnóstico completado!")
    print("📖 Revisa los logs de la aplicación para más detalles")
    print(f"{'='*50}")

if __name__ == "__main__":
    main() 