#!/usr/bin/env python3
"""
Script para reiniciar el servidor con nueva configuración de CORS
"""

import subprocess
import sys
import time
import signal
import os

def main():
    print("🔄 Reiniciando servidor con nueva configuración de CORS...")
    
    # Buscar procesos de Python que estén ejecutando main.py
    try:
        # En Windows
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'main.py' in result.stdout:
                print("⚠️  Detectado proceso de main.py ejecutándose")
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                             capture_output=True)
                print("✅ Proceso anterior terminado")
        else:
            # En Linux/Mac
            result = subprocess.run(['pgrep', '-f', 'main.py'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ Proceso {pid} terminado")
    except Exception as e:
        print(f"⚠️  No se pudo terminar procesos anteriores: {e}")
    
    # Esperar un momento
    time.sleep(2)
    
    # Reiniciar el servidor
    try:
        print("🚀 Iniciando servidor con nueva configuración...")
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")
        print("💡 Intenta ejecutar manualmente: python main.py")

if __name__ == "__main__":
    main() 