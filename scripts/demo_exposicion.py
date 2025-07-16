#!/usr/bin/env python3
"""
Script de demostración para la exposición de Cinemax API
Muestra los algoritmos en acción con ejemplos prácticos
"""

import requests
import json
import time
from typing import Dict, List, Any

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

class DemoExposicion:
    """Clase para demostrar los algoritmos durante la exposición"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def print_header(self, title: str):
        """Imprimir encabezado con formato"""
        print("\n" + "="*60)
        print(f"🎬 {title}")
        print("="*60)
    
    def print_success(self, message: str):
        """Imprimir mensaje de éxito"""
        print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Imprimir información"""
        print(f"ℹ️  {message}")
    
    def print_error(self, message: str):
        """Imprimir error"""
        print(f"❌ {message}")
    
    def demo_1_algoritmos_recursivos(self):
        """Demostración 1: Algoritmos Recursivos"""
        self.print_header("DEMOSTRACIÓN 1: ALGORITMOS RECURSIVOS")
        
        # Factorial recursivo
        self.print_info("Calculando factorial de 10 de forma recursiva...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/recursivos/factorial",
                json={"n": 10}
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Factorial de 10 = {data['factorial']}")
                self.print_info(f"Algoritmo: {data['algoritmo']}")
                self.print_info(f"Complejidad: {data['complejidad']}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
        
        # Fibonacci recursivo
        self.print_info("Calculando Fibonacci de 15 de forma recursiva...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/recursivos/fibonacci",
                json={"n": 15}
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Fibonacci de 15 = {data['fibonacci']}")
                self.print_info(f"Algoritmo: {data['algoritmo']}")
                self.print_info(f"Complejidad: {data['complejidad']}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
    
    def demo_2_algoritmos_ordenamiento(self):
        """Demostración 2: Algoritmos de Ordenamiento"""
        self.print_header("DEMOSTRACIÓN 2: ALGORITMOS DE ORDENAMIENTO")
        
        # Datos de ejemplo
        peliculas = [
            {"titulo": "Avengers", "rating": 9.0, "genero": "Acción"},
            {"titulo": "Titanic", "rating": 8.5, "genero": "Drama"},
            {"titulo": "Inception", "rating": 8.8, "genero": "Ciencia Ficción"},
            {"titulo": "The Dark Knight", "rating": 9.2, "genero": "Acción"},
            {"titulo": "Pulp Fiction", "rating": 8.9, "genero": "Crimen"}
        ]
        
        self.print_info("Ordenando películas por rating usando QuickSort...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/ordenamiento/quicksort-peliculas",
                json={"peliculas": peliculas}
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success("Películas ordenadas por QuickSort:")
                for i, pelicula in enumerate(data['peliculas_ordenadas'], 1):
                    print(f"  {i}. {pelicula['titulo']} - Rating: {pelicula['rating']}")
                self.print_info(f"Algoritmo: {data['algoritmo']}")
                self.print_info(f"Complejidad: {data['complejidad']}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
    
    def demo_3_algoritmos_busqueda(self):
        """Demostración 3: Algoritmos de Búsqueda"""
        self.print_header("DEMOSTRACIÓN 3: ALGORITMOS DE BÚSQUEDA")
        
        # Datos ordenados para búsqueda binaria
        peliculas_ordenadas = [
            {"titulo": "Avengers", "rating": 9.0},
            {"titulo": "Inception", "rating": 8.8},
            {"titulo": "Pulp Fiction", "rating": 8.9},
            {"titulo": "The Dark Knight", "rating": 9.2},
            {"titulo": "Titanic", "rating": 8.5}
        ]
        
        self.print_info("Buscando 'Inception' usando búsqueda binaria...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/busqueda/binaria-peliculas",
                json={
                    "peliculas_ordenadas": peliculas_ordenadas,
                    "titulo_buscar": "Inception"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data['pelicula_encontrada']:
                    pelicula = data['pelicula_encontrada']
                    self.print_success(f"Película encontrada: {pelicula['titulo']} - Rating: {pelicula['rating']}")
                else:
                    self.print_info("Película no encontrada")
                self.print_info(f"Algoritmo: {data['algoritmo']}")
                self.print_info(f"Complejidad: {data['complejidad']}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
        
        # Búsqueda lineal con filtros
        peliculas = [
            {"titulo": "Avengers", "rating": 9.0, "genero": "Acción", "duracion": 150, "precio": 12},
            {"titulo": "Titanic", "rating": 8.5, "genero": "Drama", "duracion": 195, "precio": 10},
            {"titulo": "Inception", "rating": 8.8, "genero": "Ciencia Ficción", "duracion": 148, "precio": 11},
            {"titulo": "The Dark Knight", "rating": 9.2, "genero": "Acción", "duracion": 152, "precio": 13},
            {"titulo": "Pulp Fiction", "rating": 8.9, "genero": "Crimen", "duracion": 154, "precio": 9}
        ]
        
        self.print_info("Búsqueda lineal con filtros (género: Acción, duración < 160)...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/busqueda/lineal-filtros",
                json={
                    "peliculas": peliculas,
                    "filtros": {
                        "genero": "Acción",
                        "duracion_max": 160
                    }
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Películas encontradas: {data['total_resultados']}")
                for pelicula in data['peliculas_encontradas']:
                    print(f"  - {pelicula['titulo']} ({pelicula['genero']}, {pelicula['duracion']}min)")
                self.print_info(f"Algoritmo: {data['algoritmo']}")
                self.print_info(f"Complejidad: {data['complejidad']}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
    
    def demo_4_integracion_flujo_real(self):
        """Demostración 4: Integración en Flujo Real"""
        self.print_header("DEMOSTRACIÓN 4: INTEGRACIÓN EN FLUJO REAL")
        
        self.print_info("Simulando flujo completo de compra con algoritmos integrados...")
        
        # Paso 1: Obtener películas con ordenamiento automático
        self.print_info("1. Obteniendo películas con ordenamiento automático...")
        try:
            response = self.session.get(f"{BASE_URL}/peliculas?ordenar_por=rating&algoritmo=quicksort")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Películas obtenidas: {len(data['peliculas'])}")
                self.print_info(f"Algoritmo aplicado: {data.get('algoritmo_utilizado', 'N/A')}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
        
        # Paso 2: Búsqueda con filtros
        self.print_info("2. Búsqueda con filtros múltiples...")
        try:
            response = self.session.post(
                f"{BASE_URL}/peliculas/buscar",
                json={
                    "genero": "Acción",
                    "duracion_max": 150,
                    "precio_max": 15
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Películas encontradas: {len(data['peliculas'])}")
                self.print_info(f"Algoritmo de búsqueda: {data.get('algoritmo_utilizado', 'N/A')}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
        
        # Paso 3: Generación QR recursiva
        self.print_info("3. Generando QR recursivo para entrada...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/recursivos/generar-qr",
                json={"datos": "ENTRADA_CINEMAX_2024_001"}
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success("QR generado exitosamente")
                self.print_info(f"Algoritmo: {data['algoritmo']}")
                self.print_info(f"Complejidad: {data['complejidad']}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
    
    def demo_5_metricas_rendimiento(self):
        """Demostración 5: Métricas de Rendimiento"""
        self.print_header("DEMOSTRACIÓN 5: MÉTRICAS DE RENDIMIENTO")
        
        # Benchmark de algoritmos
        self.print_info("Ejecutando benchmark de algoritmos...")
        try:
            response = self.session.post(
                f"{BASE_URL}/algoritmos/benchmark/rendimiento",
                json={
                    "algoritmo": "quicksort",
                    "datos": [
                        {"id": i, "valor": 100 - i} for i in range(1000)
                    ]
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success("Benchmark completado:")
                self.print_info(f"Tiempo de ejecución: {data.get('tiempo_ejecucion', 'N/A')}ms")
                self.print_info(f"Memoria utilizada: {data.get('memoria_utilizada', 'N/A')}MB")
                self.print_info(f"Complejidad teórica: {data.get('complejidad_teorica', 'N/A')}")
            else:
                self.print_error(f"Error: {response.text}")
        except Exception as e:
            self.print_error(f"Error de conexión: {e}")
    
    def run_demo_completa(self):
        """Ejecutar demostración completa"""
        print("🎬 CINEMAX API - DEMOSTRACIÓN DE ALGORITMOS")
        print("="*60)
        print("Esta demostración muestra la integración de algoritmos")
        print("en una aplicación real de gestión de cine.")
        print("="*60)
        
        # Ejecutar todas las demostraciones
        self.demo_1_algoritmos_recursivos()
        time.sleep(2)
        
        self.demo_2_algoritmos_ordenamiento()
        time.sleep(2)
        
        self.demo_3_algoritmos_busqueda()
        time.sleep(2)
        
        self.demo_4_integracion_flujo_real()
        time.sleep(2)
        
        self.demo_5_metricas_rendimiento()
        
        # Resumen final
        self.print_header("RESUMEN DE LA DEMOSTRACIÓN")
        self.print_success("✅ Algoritmos recursivos funcionando")
        self.print_success("✅ Algoritmos de ordenamiento optimizados")
        self.print_success("✅ Algoritmos de búsqueda eficientes")
        self.print_success("✅ Integración transparente en flujo real")
        self.print_success("✅ Métricas de rendimiento disponibles")
        
        print("\n🎯 Puntos Clave:")
        print("  • Los algoritmos se ejecutan automáticamente")
        print("  • No requiere intervención manual del usuario")
        print("  • Optimización de rendimiento transparente")
        print("  • Fallbacks inteligentes para robustez")
        print("  • Arquitectura escalable y mantenible")
        
        print("\n🚀 Cinemax API demuestra que los algoritmos")
        print("   no son solo teoría, sino herramientas poderosas")
        print("   para aplicaciones reales de producción.")

if __name__ == "__main__":
    demo = DemoExposicion()
    demo.run_demo_completa() 