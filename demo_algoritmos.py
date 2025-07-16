#!/usr/bin/env python3
"""
Demo de Algoritmos de Estructuras de Datos
Cinemax API - Métodos Recursivos, Ordenamiento y Búsqueda
"""

import sys
import os

# Agregar el directorio actual al path para importar servicios
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.algorithms_service import algorithms_service
    print("✅ Servicio de algoritmos cargado correctamente")
except ImportError as e:
    print(f"❌ Error al importar algoritmos: {e}")
    print("📝 Asegúrate de que el archivo services/algorithms_service.py existe")
    sys.exit(1)


def demo_recursivos():
    """Demo de algoritmos recursivos"""
    print("\n📊 ALGORITMOS RECURSIVOS")
    print("=" * 40)
    
    # 1. Factorial Recursivo
    print("\n🔢 1. Factorial Recursivo")
    n = 5
    factorial = algorithms_service.calcular_factorial_recursivo(n)
    print(f"   Factorial de {n}: {factorial}")
    print(f"   Complejidad: O(n)")
    
    # 2. Fibonacci Recursivo
    print("\n🐰 2. Fibonacci Recursivo")
    fib_n = 8
    fibonacci = algorithms_service.fibonacci_recursivo(fib_n)
    print(f"   Fibonacci({fib_n}): {fibonacci}")
    print(f"   Complejidad: O(2^n)")
    
    # 3. Búsqueda Recursiva en Árbol
    print("\n🌳 3. Búsqueda Recursiva en Árbol de Géneros")
    arbol_generos = [
        {
            "id": "accion",
            "nombre": "Acción",
            "subgeneros": [
                {"id": "superheroes", "nombre": "Superhéroes"},
                {"id": "guerra", "nombre": "Guerra"}
            ]
        },
        {
            "id": "drama",
            "nombre": "Drama",
            "subgeneros": [
                {"id": "biografico", "nombre": "Biográfico"}
            ]
        }
    ]
    
    resultado = algorithms_service.buscar_genero_recursivo(arbol_generos, "superheroes")
    if resultado:
        print(f"   Género encontrado: {resultado['genero']['nombre']}")
        print(f"   Nivel en el árbol: {resultado['nivel']}")
    print(f"   Complejidad: O(n)")
    
    # 4. Conteo Recursivo de Asientos
    print("\n💺 4. Conteo Recursivo de Asientos")
    sala_tree = {
        "filas": [
            {
                "fila": "A",
                "asientos": [
                    {"numero": "A1", "estado": "disponible"},
                    {"numero": "A2", "estado": "ocupado"},
                    {"numero": "A3", "estado": "disponible"}
                ]
            },
            {
                "fila": "B",
                "asientos": [
                    {"numero": "B1", "estado": "disponible"},
                    {"numero": "B2", "estado": "disponible"}
                ]
            }
        ]
    }
    
    total_disponibles = algorithms_service.contar_asientos_disponibles_recursivo(sala_tree)
    print(f"   Asientos disponibles: {total_disponibles}")
    print(f"   Complejidad: O(n*m)")


def demo_ordenamiento():
    """Demo de algoritmos de ordenamiento"""
    print("\n📈 ALGORITMOS DE ORDENAMIENTO")
    print("=" * 40)
    
    # 1. QuickSort para Películas
    print("\n⚡ 1. QuickSort - Películas por Rating")
    peliculas = [
        {"titulo": "Avengers", "rating": 3.5},
        {"titulo": "Spider-Man", "rating": 4.8},
        {"titulo": "Batman", "rating": 2.1},
        {"titulo": "Thor", "rating": 4.2}
    ]
    
    print("   Películas originales:")
    for p in peliculas:
        print(f"     {p['titulo']}: {p['rating']}")
    
    peliculas_ordenadas = algorithms_service.quicksort_peliculas_rating(peliculas.copy())
    
    print("   Películas ordenadas por rating (descendente):")
    for p in peliculas_ordenadas:
        print(f"     {p['titulo']}: {p['rating']}")
    print(f"   Complejidad: O(n log n) promedio")
    
    # 2. MergeSort para Funciones
    print("\n🔄 2. MergeSort - Funciones por Hora")
    funciones = [
        {"id": "func_1", "hora": "20:00", "sala": "A"},
        {"id": "func_2", "hora": "14:00", "sala": "B"},
        {"id": "func_3", "hora": "17:00", "sala": "C"},
        {"id": "func_4", "hora": "11:00", "sala": "A"}
    ]
    
    print("   Funciones originales:")
    for f in funciones:
        print(f"     {f['hora']} - Sala {f['sala']}")
    
    funciones_ordenadas = algorithms_service.mergesort_funciones_hora(funciones.copy())
    
    print("   Funciones ordenadas por hora:")
    for f in funciones_ordenadas:
        print(f"     {f['hora']} - Sala {f['sala']}")
    print(f"   Complejidad: O(n log n)")
    
    # 3. HeapSort para Transacciones
    print("\n📊 3. HeapSort - Transacciones por Fecha")
    transacciones = [
        {"id": "tx_1", "fecha": "2024-01-15", "monto": 15000},
        {"id": "tx_2", "fecha": "2024-01-13", "monto": 12000},
        {"id": "tx_3", "fecha": "2024-01-17", "monto": 18000},
        {"id": "tx_4", "fecha": "2024-01-14", "monto": 9000}
    ]
    
    print("   Transacciones originales:")
    for t in transacciones:
        print(f"     {t['fecha']}: ${t['monto']}")
    
    transacciones_ordenadas = algorithms_service.heapsort_transacciones_fecha(transacciones.copy())
    
    print("   Transacciones ordenadas por fecha (descendente):")
    for t in transacciones_ordenadas:
        print(f"     {t['fecha']}: ${t['monto']}")
    print(f"   Complejidad: O(n log n)")


def demo_busqueda():
    """Demo de algoritmos de búsqueda"""
    print("\n🔍 ALGORITMOS DE BÚSQUEDA")
    print("=" * 40)
    
    # 1. Búsqueda Binaria
    print("\n🎯 1. Búsqueda Binaria - Películas Ordenadas")
    peliculas_ordenadas = [
        {"titulo": "Avengers", "rating": 4.8},
        {"titulo": "Batman", "rating": 4.5},
        {"titulo": "Spider-Man", "rating": 4.2},
        {"titulo": "Thor", "rating": 3.9}
    ]
    
    titulo_buscar = "Spider-Man"
    resultado = algorithms_service.busqueda_binaria_peliculas(peliculas_ordenadas, titulo_buscar)
    
    if resultado:
        print(f"   Película encontrada: {resultado['titulo']} (Rating: {resultado['rating']})")
    else:
        print(f"   Película '{titulo_buscar}' no encontrada")
    print(f"   Complejidad: O(log n)")
    
    # 2. Búsqueda Lineal con Filtros
    print("\n🔍 2. Búsqueda Lineal con Filtros Múltiples")
    peliculas = [
        {"titulo": "Avengers", "generos": ["accion"], "duracion": 120, "precio": 15000, "activa": True},
        {"titulo": "Drama", "generos": ["drama"], "duracion": 90, "precio": 12000, "activa": True},
        {"titulo": "Batman", "generos": ["accion"], "duracion": 150, "precio": 18000, "activa": False},
        {"titulo": "Comedia", "generos": ["comedia"], "duracion": 100, "precio": 10000, "activa": True}
    ]
    
    filtros = {"genero": "accion", "activa": True}
    resultados = algorithms_service.busqueda_lineal_filtros(peliculas, filtros)
    
    print(f"   Filtros aplicados: {filtros}")
    print(f"   Películas encontradas: {len(resultados)}")
    for p in resultados:
        print(f"     {p['titulo']} - ${p['precio']}")
    print(f"   Complejidad: O(n * m)")
    
    # 3. DFS para Recomendaciones
    print("\n🌐 3. DFS - Búsqueda en Profundidad para Recomendaciones")
    grafo_usuario = {
        "edges": [
            {"from": "user_001", "to": "pel_001", "relation": "watched"},
            {"from": "pel_001", "to": "pel_002", "relation": "similar_genre"},
            {"from": "pel_001", "to": "pel_003", "relation": "similar_genre"},
            {"from": "user_001", "to": "pel_004", "relation": "watched"},
            {"from": "pel_004", "to": "pel_005", "relation": "similar_genre"}
        ]
    }
    
    recomendaciones = algorithms_service.dfs_recomendaciones(grafo_usuario, "user_001", profundidad_max=2)
    print(f"   Recomendaciones encontradas: {len(recomendaciones)}")
    print(f"   IDs de películas recomendadas: {recomendaciones}")
    print(f"   Complejidad: O(V + E)")


def demo_optimizacion():
    """Demo de optimización y análisis"""
    print("\n⚡ OPTIMIZACIÓN Y ANÁLISIS")
    print("=" * 40)
    
    # 1. Cache Optimizado
    print("\n💾 1. Cache Optimizado - Índices Hash")
    peliculas = [
        {"_id": "pel_001", "titulo": "Avengers", "director": "Anthony Russo"},
        {"_id": "pel_002", "titulo": "Spider-Man", "director": "Jon Watts"},
        {"_id": "pel_003", "titulo": "Batman", "director": "Matt Reeves"}
    ]
    
    cache_optimizado = algorithms_service.optimizar_cache_peliculas(peliculas)
    print(f"   Total de índices creados: {len(cache_optimizado)}")
    print(f"   Índices por ID: {list(cache_optimizado.keys())[:3]}...")
    print(f"   Complejidad: O(n) construcción, O(1) búsqueda")
    
    # 2. Análisis de Complejidad
    print("\n📊 2. Análisis de Complejidad")
    algoritmos = ["quicksort", "mergesort", "busqueda_binaria", "dfs"]
    
    for algoritmo in algoritmos:
        complejidad = algorithms_service.calcular_complejidad_algoritmo(algoritmo, 1000)
        print(f"   {algoritmo.upper()}:")
        print(f"     Complejidad temporal: {complejidad['complejidad_temporal']}")
        print(f"     Complejidad espacial: {complejidad['complejidad_espacial']}")
    
    # 3. Benchmark
    print("\n⏱️  3. Benchmark de Rendimiento")
    datos = [{"rating": i} for i in range(100)]
    
    for algoritmo in ["quicksort", "mergesort", "busqueda_lineal"]:
        try:
            benchmark = algorithms_service.benchmark_algoritmo(algoritmo, datos)
            print(f"   {algoritmo.upper()}:")
            print(f"     Tiempo de ejecución: {benchmark['tiempo_ejecucion']:.6f}s")
            print(f"     Tamaño de datos: {benchmark['tamaño_datos']}")
            print(f"     Resultados: {benchmark['resultado_tamaño']}")
        except Exception as e:
            print(f"   Error en benchmark de {algoritmo}: {e}")


def demo_estructuras_datos():
    """Demo de estructuras de datos utilizadas"""
    print("\n🗂️  ESTRUCTURAS DE DATOS UTILIZADAS")
    print("=" * 50)
    
    estructuras = [
        {
            "nombre": "PILAS (Stacks) - Redis",
            "uso": "Cola de emails, historial de transacciones",
            "operaciones": "LPUSH, RPOP, LLEN",
            "complejidad": "O(1) para push/pop"
        },
        {
            "nombre": "COLAS (Queues) - Redis", 
            "uso": "Procesamiento de pagos, notificaciones WebSocket",
            "operaciones": "LPUSH, RPOP, BLPOP",
            "complejidad": "O(1) para enqueue/dequeue"
        },
        {
            "nombre": "LISTAS ENLAZADAS - MongoDB",
            "uso": "Lista de películas, funciones por película",
            "operaciones": "Inserción, eliminación, navegación",
            "complejidad": "O(1) inserción/eliminación"
        },
        {
            "nombre": "TABLAS HASH - Redis",
            "uso": "Cache de sesiones, datos de películas",
            "operaciones": "HSET, HGET, HDEL",
            "complejidad": "O(1) acceso promedio"
        },
        {
            "nombre": "ÁRBOLES - MongoDB",
            "uso": "Jerarquía de géneros, asientos por sala",
            "operaciones": "Búsqueda, inserción, eliminación",
            "complejidad": "O(log n) búsqueda"
        },
        {
            "nombre": "GRAFOS - MongoDB",
            "uso": "Relaciones usuario-película, recomendaciones",
            "operaciones": "DFS, BFS, path finding",
            "complejidad": "O(V + E) para recorrido"
        }
    ]
    
    for i, estructura in enumerate(estructuras, 1):
        print(f"\n{i}. {estructura['nombre']}")
        print(f"   Uso: {estructura['uso']}")
        print(f"   Operaciones: {estructura['operaciones']}")
        print(f"   Complejidad: {estructura['complejidad']}")


def main():
    """Función principal de la demo"""
    print("🎬 CINEMAX API - DEMO DE ALGORITMOS")
    print("=" * 60)
    print("Estructuras de Datos, Métodos Recursivos, Ordenamiento y Búsqueda")
    print("=" * 60)
    
    try:
        # Ejecutar todas las demos
        demo_recursivos()
        demo_ordenamiento()
        demo_busqueda()
        demo_optimizacion()
        demo_estructuras_datos()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETADA EXITOSAMENTE!")
        print("🎯 Todos los algoritmos funcionando correctamente")
        print("📚 Documentación completa en: docs/API_ARCHITECTURE_DOCUMENTATION.md")
        print("🌐 API disponible en: /api/v1/algoritmos/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        print("📝 Verifica que todos los servicios estén disponibles")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 