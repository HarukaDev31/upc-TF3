#!/usr/bin/env python3
"""
Script para diagnosticar problemas con Docker y la API
"""

import subprocess
import requests
import time
import json

def check_docker_status():
    """Verifica el estado de Docker"""
    print("🔍 Verificando estado de Docker...")
    
    try:
        # Verificar si Docker está corriendo
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker instalado: {result.stdout.strip()}")
        else:
            print("❌ Docker no está instalado o no está en el PATH")
            return False
            
        # Verificar si Docker daemon está corriendo
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker daemon está corriendo")
        else:
            print("❌ Docker daemon no está corriendo")
            return False
            
        return True
        
    except FileNotFoundError:
        print("❌ Docker no está instalado")
        return False
    except Exception as e:
        print(f"💥 Error al verificar Docker: {e}")
        return False

def check_containers():
    """Verifica los contenedores corriendo"""
    print("\n🔍 Verificando contenedores...")
    
    try:
        # Listar contenedores corriendo
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Contenedores corriendo:")
            print(result.stdout)
        else:
            print("❌ Error al listar contenedores")
            
        # Listar todos los contenedores (incluyendo los detenidos)
        result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Todos los contenedores:")
            print(result.stdout)
            
    except Exception as e:
        print(f"💥 Error al verificar contenedores: {e}")

def check_ports():
    """Verifica puertos en uso"""
    print("\n🔍 Verificando puertos...")
    
    try:
        # Verificar puerto 8000
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            port_8000_lines = [line for line in lines if ':8000' in line]
            if port_8000_lines:
                print("📋 Puerto 8000 en uso:")
                for line in port_8000_lines:
                    print(f"   {line}")
            else:
                print("✅ Puerto 8000 libre")
                
    except Exception as e:
        print(f"💥 Error al verificar puertos: {e}")

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print("\n🔍 Probando endpoints de la API...")
    
    endpoints = [
        "http://localhost:8000/",
        "http://localhost:8000/health",
        "http://localhost:8000/test",
        "http://localhost:8000/api/v1/peliculas"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🌐 Probando: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Content-Type: {response.headers.get('content-type', 'No especificado')}")
            
            if response.status_code == 200:
                print("✅ Endpoint responde correctamente")
                try:
                    data = response.json()
                    print(f"📄 Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"📄 Respuesta: {response.text[:200]}...")
            else:
                print(f"❌ Error HTTP {response.status_code}")
                print(f"📄 Contenido: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ No se pudo conectar a {endpoint}")
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout al conectar a {endpoint}")
        except Exception as e:
            print(f"💥 Error inesperado: {e}")

def check_docker_logs():
    """Verifica los logs del contenedor de la API"""
    print("\n🔍 Verificando logs del contenedor...")
    
    try:
        # Verificar logs del contenedor de la API
        result = subprocess.run(['docker', 'logs', 'cinemax_api'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Logs del contenedor cinemax_api:")
            print(result.stdout[-500:])  # Últimas 500 líneas
        else:
            print("❌ No se pudieron obtener logs del contenedor")
            
    except Exception as e:
        print(f"💥 Error al obtener logs: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando diagnóstico de Docker y API...")
    print("=" * 60)
    
    # Verificar Docker
    if not check_docker_status():
        print("\n❌ Docker no está disponible. Instala Docker Desktop.")
        return
    
    # Verificar contenedores
    check_containers()
    
    # Verificar puertos
    check_ports()
    
    # Verificar logs
    check_docker_logs()
    
    # Probar endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("🎉 Diagnóstico completado!")
    print("\n💡 Si la API no responde, verifica:")
    print("   1. Que Docker esté corriendo")
    print("   2. Que los contenedores estén saludables")
    print("   3. Que el puerto 8000 no esté bloqueado")
    print("   4. Los logs del contenedor para errores")

if __name__ == "__main__":
    main() 