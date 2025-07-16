"""
Test para algoritmos de estructuras de datos
Demuestra métodos recursivos, ordenamiento y búsqueda
"""

import pytest
from services.algorithms_service import algorithms_service


class TestAlgoritmosRecursivos:
    """Test para métodos recursivos"""
    
    def test_buscar_genero_recursivo(self):
        """Test búsqueda recursiva en árbol de géneros"""
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
        assert resultado is not None
        assert resultado['genero']['id'] == "superheroes"
        assert resultado['nivel'] == 1
    
    def test_contar_asientos_disponibles_recursivo(self):
        """Test conteo recursivo de asientos"""
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
        
        total = algorithms_service.contar_asientos_disponibles_recursivo(sala_tree)
        assert total == 4  # A1, A3, B1, B2
    
    def test_calcular_factorial_recursivo(self):
        """Test factorial recursivo"""
        resultado = algorithms_service.calcular_factorial_recursivo(5)
        assert resultado == 120  # 5! = 5 * 4 * 3 * 2 * 1 = 120
    
    def test_fibonacci_recursivo(self):
        """Test Fibonacci recursivo"""
        resultado = algorithms_service.fibonacci_recursivo(8)
        assert resultado == 21  # F(8) = 21


class TestAlgoritmosOrdenamiento:
    """Test para métodos de ordenamiento"""
    
    def test_quicksort_peliculas_rating(self):
        """Test QuickSort para películas por rating"""
        peliculas = [
            {"titulo": "Película A", "rating": 3.5},
            {"titulo": "Película B", "rating": 4.8},
            {"titulo": "Película C", "rating": 2.1},
            {"titulo": "Película D", "rating": 4.2}
        ]
        
        peliculas_ordenadas = algorithms_service.quicksort_peliculas_rating(peliculas.copy())
        
        # Verificar orden descendente por rating
        ratings = [p['rating'] for p in peliculas_ordenadas]
        assert ratings == [4.8, 4.2, 3.5, 2.1]
    
    def test_mergesort_funciones_hora(self):
        """Test MergeSort para funciones por hora"""
        funciones = [
            {"id": "func_1", "hora": "20:00", "sala": "A"},
            {"id": "func_2", "hora": "14:00", "sala": "B"},
            {"id": "func_3", "hora": "17:00", "sala": "C"},
            {"id": "func_4", "hora": "11:00", "sala": "A"}
        ]
        
        funciones_ordenadas = algorithms_service.mergesort_funciones_hora(funciones.copy())
        
        # Verificar orden cronológico
        horas = [f['hora'] for f in funciones_ordenadas]
        assert horas == ["11:00", "14:00", "17:00", "20:00"]
    
    def test_heapsort_transacciones_fecha(self):
        """Test HeapSort para transacciones por fecha"""
        transacciones = [
            {"id": "tx_1", "fecha_transaccion": "2024-01-15", "monto": 15000},
            {"id": "tx_2", "fecha_transaccion": "2024-01-13", "monto": 12000},
            {"id": "tx_3", "fecha_transaccion": "2024-01-17", "monto": 18000},
            {"id": "tx_4", "fecha_transaccion": "2024-01-14", "monto": 9000}
        ]
        
        transacciones_ordenadas = algorithms_service.heapsort_transacciones_fecha(transacciones.copy())
        
        # Verificar orden cronológico descendente
        fechas = [t['fecha_transaccion'] for t in transacciones_ordenadas]
        assert fechas == ["2024-01-17", "2024-01-15", "2024-01-14", "2024-01-13"]


class TestAlgoritmosBusqueda:
    """Test para métodos de búsqueda"""
    
    def test_busqueda_binaria_peliculas(self):
        """Test búsqueda binaria en películas ordenadas"""
        peliculas_ordenadas = [
            {"titulo": "Avengers", "rating": 4.8},
            {"titulo": "Batman", "rating": 4.5},
            {"titulo": "Spider-Man", "rating": 4.2},
            {"titulo": "Thor", "rating": 3.9}
        ]
        
        resultado = algorithms_service.busqueda_binaria_peliculas(peliculas_ordenadas, "Spider-Man")
        assert resultado is not None
        assert resultado['titulo'] == "Spider-Man"
    
    def test_busqueda_lineal_filtros(self):
        """Test búsqueda lineal con filtros múltiples"""
        peliculas = [
            {"titulo": "Película A", "generos": ["accion"], "duracion_minutos": 120, "precio_base": 15000, "activa": True},
            {"titulo": "Película B", "generos": ["drama"], "duracion_minutos": 90, "precio_base": 12000, "activa": True},
            {"titulo": "Película C", "generos": ["accion"], "duracion_minutos": 150, "precio_base": 18000, "activa": False},
            {"titulo": "Película D", "generos": ["comedia"], "duracion_minutos": 100, "precio_base": 10000, "activa": True}
        ]
        
        filtros = {"genero": "accion", "activa": True}
        resultados = algorithms_service.busqueda_lineal_filtros(peliculas, filtros)
        
        assert len(resultados) == 1
        assert resultados[0]['titulo'] == "Película A"
    
    def test_dfs_recomendaciones(self):
        """Test búsqueda en profundidad para recomendaciones"""
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
        
        # Debería encontrar pel_002, pel_003, pel_005
        assert len(recomendaciones) >= 2
        assert "pel_002" in recomendaciones or "pel_003" in recomendaciones


class TestAlgoritmosOptimizacion:
    """Test para métodos de optimización"""
    
    def test_optimizar_cache_peliculas(self):
        """Test optimización de cache de películas"""
        peliculas = [
            {"_id": "pel_001", "titulo": "Avengers", "director": "Anthony Russo"},
            {"_id": "pel_002", "titulo": "Spider-Man", "director": "Jon Watts"},
            {"_id": "pel_003", "titulo": "Batman", "director": "Matt Reeves"}
        ]
        
        cache_optimizado = algorithms_service.optimizar_cache_peliculas(peliculas)
        
        # Verificar índices
        assert "pel_001" in cache_optimizado
        assert "avengers" in cache_optimizado
        assert "anthony russo" in cache_optimizado
    
    def test_calcular_complejidad_algoritmo(self):
        """Test cálculo de complejidad"""
        complejidad = algorithms_service.calcular_complejidad_algoritmo("quicksort", 100)
        
        assert complejidad['algoritmo'] == "quicksort"
        assert complejidad['complejidad_temporal'] == "O(n log n)"
        assert complejidad['tamaño_entrada'] == 100
    
    def test_benchmark_algoritmo(self):
        """Test benchmark de algoritmos"""
        datos = [{"rating": i} for i in range(100)]
        
        benchmark = algorithms_service.benchmark_algoritmo("quicksort", datos)
        
        assert benchmark['algoritmo'] == "quicksort"
        assert benchmark['tamaño_datos'] == 100
        assert benchmark['tiempo_ejecucion'] > 0


def test_demo_completa():
    """Demo completa de todos los algoritmos"""
    print("\n🧮 DEMO COMPLETA DE ALGORITMOS")
    print("=" * 50)
    
    # 1. Algoritmos Recursivos
    print("\n📊 1. ALGORITMOS RECURSIVOS")
    print("-" * 30)
    
    # Factorial
    n = 5
    factorial = algorithms_service.calcular_factorial_recursivo(n)
    print(f"Factorial de {n}: {factorial}")
    
    # Fibonacci
    fib_n = 8
    fibonacci = algorithms_service.fibonacci_recursivo(fib_n)
    print(f"Fibonacci({fib_n}): {fibonacci}")
    
    # 2. Algoritmos de Ordenamiento
    print("\n📈 2. ALGORITMOS DE ORDENAMIENTO")
    print("-" * 30)
    
    # QuickSort
    peliculas = [
        {"titulo": "A", "rating": 3.5},
        {"titulo": "B", "rating": 4.8},
        {"titulo": "C", "rating": 2.1}
    ]
    peliculas_ordenadas = algorithms_service.quicksort_peliculas_rating(peliculas.copy())
    print(f"QuickSort - Películas ordenadas por rating: {[p['rating'] for p in peliculas_ordenadas]}")
    
    # 3. Algoritmos de Búsqueda
    print("\n🔍 3. ALGORITMOS DE BÚSQUEDA")
    print("-" * 30)
    
    # Búsqueda lineal con filtros
    peliculas = [
        {"titulo": "A", "generos": ["accion"], "activa": True},
        {"titulo": "B", "generos": ["drama"], "activa": True},
        {"titulo": "C", "generos": ["accion"], "activa": False}
    ]
    resultados = algorithms_service.busqueda_lineal_filtros(peliculas, {"genero": "accion", "activa": True})
    print(f"Búsqueda lineal - Películas de acción activas: {len(resultados)} encontradas")
    
    # 4. Optimización
    print("\n⚡ 4. OPTIMIZACIÓN")
    print("-" * 30)
    
    cache = algorithms_service.optimizar_cache_peliculas(peliculas)
    print(f"Cache optimizado - {len(cache)} índices creados")
    
    # 5. Análisis de Complejidad
    print("\n📊 5. ANÁLISIS DE COMPLEJIDAD")
    print("-" * 30)
    
    complejidad = algorithms_service.calcular_complejidad_algoritmo("quicksort", 1000)
    print(f"QuickSort - Complejidad temporal: {complejidad['complejidad_temporal']}")
    
    print("\n✅ Demo completada exitosamente!")


if __name__ == "__main__":
    # Ejecutar demo
    test_demo_completa() 