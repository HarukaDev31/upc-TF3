#!/usr/bin/env python3
"""
Script de configuración inicial para el Sistema de Cine
"""

import os
import sys
import subprocess
import platform


def print_header():
    """Imprime el header del proyecto"""
    print("🎬" + "="*60 + "🎬")
    print("    SISTEMA DE CINE - CONFIGURACIÓN INICIAL")
    print("🎬" + "="*60 + "🎬")
    print()


def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 9):
        print("❌ Error: Se requiere Python 3.9 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detectado")


def check_command_exists(command):
    """Verifica si un comando existe en el sistema"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_wsl_available():
    """Verifica si WSL está disponible en Windows"""
    if platform.system() != "Windows":
        return False
    
    try:
        result = subprocess.run(["wsl", "--list", "--quiet"], 
                              capture_output=True, text=True, check=True)
        return len(result.stdout.strip()) > 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_redis_in_wsl():
    """Verifica si Redis está disponible en WSL"""
    try:
        result = subprocess.run(["wsl", "redis-server", "--version"], 
                              capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_docker_in_wsl():
    """Verifica si Docker está disponible en WSL"""
    try:
        result = subprocess.run(["wsl", "docker", "--version"], 
                              capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_mongodb_docker():
    """Verifica si MongoDB está corriendo en Docker"""
    try:
        result = subprocess.run(["wsl", "docker", "ps", "--filter", "name=mongodb", "--format", "{{.Names}}"], 
                              capture_output=True, text=True, check=True)
        return "mongodb" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_dependencies():
    """Verifica dependencias del sistema"""
    print("\n📋 Verificando dependencias del sistema...")
    
    # Dependencias básicas
    basic_deps = {
        "git": "Git"
    }
    
    missing = []
    
    # Verificar dependencias básicas
    for cmd, name in basic_deps.items():
        if check_command_exists(cmd):
            print(f"✅ {name} encontrado")
        else:
            print(f"❌ {name} NO encontrado")
            missing.append(name)
    
    # Verificar Redis en WSL (preferido en Windows)
    if platform.system() == "Windows":
        if check_wsl_available():
            print("✅ WSL detectado")
            if check_redis_in_wsl():
                print("✅ Redis en WSL encontrado")
            else:
                print("❌ Redis NO encontrado en WSL")
                print("   💡 Tip: Instala Redis en WSL con: wsl sudo apt install redis-server")
                missing.append("Redis en WSL")
        else:
            print("❌ WSL no disponible")
            print("   💡 Tip: Instala WSL para mejor compatibilidad con Redis")
            # Fallback a Redis nativo de Windows
            if check_command_exists("redis-server"):
                print("✅ Redis Server (Windows) encontrado como fallback")
            else:
                print("❌ Redis Server NO encontrado")
                missing.append("Redis Server")
    else:
        # En Linux/Mac, verificar Redis normal
        if check_command_exists("redis-server"):
            print("✅ Redis Server encontrado")
        else:
            print("❌ Redis Server NO encontrado")
            missing.append("Redis Server")
    
    # Verificar MongoDB con Docker en WSL
    if platform.system() == "Windows" and check_wsl_available():
        if check_docker_in_wsl():
            print("✅ Docker en WSL encontrado")
            if check_mongodb_docker():
                print("✅ MongoDB en Docker (WSL) encontrado")
            else:
                print("❌ MongoDB NO está corriendo en Docker")
                print("   💡 Tip: Inicia MongoDB con Docker: wsl docker run -d --name mongodb -p 27017:27017 mongo:latest")
                missing.append("MongoDB en Docker")
        else:
            print("❌ Docker NO encontrado en WSL")
            print("   💡 Tip: Instala Docker en WSL para MongoDB")
            missing.append("Docker en WSL")
    else:
        # Verificar MongoDB nativo
        mongo_commands = ["mongod", "brew services list | grep mongodb"]
        mongo_found = False
        
        for cmd in mongo_commands:
            if check_command_exists(cmd.split()[0]):
                print("✅ MongoDB encontrado")
                mongo_found = True
                break
        
        if not mongo_found:
            print("❌ MongoDB NO encontrado")
            missing.append("MongoDB")
    
    if missing:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        print("   Consulta el README.md para instrucciones de instalación")
    
    return len(missing) == 0


def create_virtual_environment():
    """Crea el entorno virtual"""
    print("\n🐍 Creando entorno virtual...")
    
    if os.path.exists("venv"):
        print("✅ Entorno virtual ya existe")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando entorno virtual: {e}")
        return False


def activate_and_install():
    """Instala las dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    # Determinar el comando de activación según el OS
    if platform.system() == "Windows":
        pip_cmd = os.path.join("venv", "Scripts", "pip")
        python_cmd = os.path.join("venv", "Scripts", "python")
    else:
        pip_cmd = os.path.join("venv", "bin", "pip")
        python_cmd = os.path.join("venv", "bin", "python")
    
    try:
        # Actualizar pip
        subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ pip actualizado")
        
        # Instalar dependencias
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


def get_wsl_ip():
    """Obtiene la IP de WSL para conectar desde Windows"""
    try:
        result = subprocess.run(["wsl", "hostname", "-I"], 
                              capture_output=True, text=True, check=True)
        wsl_ip = result.stdout.strip().split()[0]
        return wsl_ip
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "localhost"


def create_env_file():
    """Crea el archivo .env si no existe"""
    print("\n⚙️  Configurando archivo de entorno...")
    
    if os.path.exists(".env"):
        print("✅ Archivo .env ya existe")
        return
    
    # Configurar Redis según el sistema
    redis_host = "localhost"
    redis_config_note = ""
    mongo_config_note = ""
    
    if platform.system() == "Windows" and check_wsl_available():
        wsl_ip = get_wsl_ip()
        redis_host = wsl_ip
        redis_config_note = f"""
# Redis en WSL Configuration
# Si Redis está en WSL, usar la IP: {wsl_ip}
# Alternativamente, usar 'localhost' si WSL2 tiene port forwarding habilitado
"""
        mongo_config_note = f"""
# MongoDB en Docker (WSL) Configuration
# MongoDB está corriendo en Docker dentro de WSL
# Puerto 27017 está mapeado desde WSL a Windows
"""
        print(f"🔧 Configurando Redis para WSL (IP: {wsl_ip})")
        print("🔧 Configurando MongoDB para Docker en WSL")
    
    env_content = f"""# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=cinemax
{redis_config_note}{mongo_config_note}
# Redis Configuration
REDIS_HOST={redis_host}
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Application Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Cine
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# External Services
PAYMENT_GATEWAY_URL=https://api.payment-provider.com
PAYMENT_GATEWAY_API_KEY=tu-api-key-del-gateway

# Metrics
ENABLE_METRICS=true
METRICS_PORT=8000

# Performance
REDIS_POOL_MAX_CONNECTIONS=50
MONGODB_MAX_CONNECTIONS=100
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Archivo .env creado exitosamente")
        
        if platform.system() == "Windows" and check_wsl_available():
            print("💡 Nota: Si tienes problemas de conexión, prueba cambiar REDIS_HOST a 'localhost'")
            
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")


def print_next_steps():
    """Imprime los siguientes pasos"""
    print("\n🚀 ¡Configuración completada!")
    print("\n📋 Siguientes pasos:")
    
    # Instrucciones específicas para cada sistema
    if platform.system() == "Windows" and check_wsl_available():
        print("   1. Iniciar Redis en WSL:")
        print("      wsl sudo systemctl start redis-server")
        print("   2. Verificar Redis:")
        print("      wsl redis-cli ping")
        print("      (Debería responder: PONG)")
        print("   3. Asegúrate de que MongoDB esté ejecutándose")
    elif platform.system() == "Windows":
        print("   1. Iniciar Redis (Windows):")
        print("      redis-server")
        print("   2. Asegúrate de que MongoDB esté ejecutándose")
    else:
        print("   1. Asegúrate de que Redis y MongoDB estén ejecutándose:")
        print("      sudo systemctl start redis-server")
        print("      sudo systemctl start mongod")
    
    print(f"   {2 if platform.system() != 'Windows' or not check_wsl_available() else 4}. Activa el entorno virtual:")
    
    if platform.system() == "Windows":
        print("      venv\\Scripts\\activate")
    else:
        print("      source venv/bin/activate")
    
    step_num = 3 if platform.system() != 'Windows' or not check_wsl_available() else 5
    print(f"   {step_num}. Ejecuta la aplicación:")
    print("      python main.py")
    print(f"   {step_num + 1}. Visita http://localhost:8000 en tu navegador")
    print(f"   {step_num + 2}. Documentación API: http://localhost:8000/docs")
    
    if platform.system() == "Windows" and check_wsl_available():
        print("\n💡 Tips para WSL:")
        print("   • Si hay problemas de conexión, edita .env y cambia REDIS_HOST=localhost")
        print("   • Para ver logs de Redis: wsl sudo journalctl -u redis-server -f")
        print("   • Para verificar IP de WSL: wsl hostname -I")
    
    print("\n🎬 ¡Disfruta del Sistema de Cine!")


def main():
    """Función principal"""
    print_header()
    
    # Verificaciones
    check_python_version()
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n⚠️  Algunas dependencias faltan. El proyecto podría no funcionar correctamente.")
        response = input("¿Continuar de todos modos? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelado.")
            sys.exit(1)
    
    # Configuración
    if not create_virtual_environment():
        sys.exit(1)
    
    if not activate_and_install():
        sys.exit(1)
    
    create_env_file()
    
    print_next_steps()


if __name__ == "__main__":
    main() 