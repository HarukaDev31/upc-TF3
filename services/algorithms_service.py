"""
Servicio de Algoritmos para Cinemax API
Implementa métodos recursivos, ordenamiento y búsqueda
"""

import qrcode
from typing import List, Dict, Any, Optional, Set
from datetime import datetime


class AlgorithmsService:
    """Servicio que implementa algoritmos de estructuras de datos"""
    
    def __init__(self):
        self.cache_algoritmos = {}
    
    # ==================== MÉTODOS RECURSIVOS ====================
    
    def buscar_genero_recursivo(self, arbol_generos: List[Dict], genero_buscar: str, nivel: int = 0) -> Optional[Dict]:
        """
        Búsqueda recursiva en árbol de géneros
        Complejidad: O(n) donde n es el número de nodos
        """
        if not arbol_generos:
            return None
        
        # Buscar en el nivel actual
        for genero in arbol_generos:
            if genero['id'] == genero_buscar:
                return {'genero': genero, 'nivel': nivel}
            
            # Búsqueda recursiva en subgéneros
            if 'subgeneros' in genero:
                resultado = self.buscar_genero_recursivo(
                    genero['subgeneros'], 
                    genero_buscar, 
                    nivel + 1
                )
                if resultado:
                    return resultado
        
        return None
    
    def contar_asientos_disponibles_recursivo(self, sala_tree: Dict, fila_actual: int = 0, asiento_actual: int = 0) -> int:
        """
        Contar asientos disponibles de forma recursiva
        Complejidad: O(n*m) donde n=filas, m=asientos por fila
        """
        if fila_actual >= len(sala_tree['filas']):
            return 0
        
        fila = sala_tree['filas'][fila_actual]
        
        if asiento_actual >= len(fila['asientos']):
            # Pasar a la siguiente fila
            return self.contar_asientos_disponibles_recursivo(sala_tree, fila_actual + 1, 0)
        
        asiento = fila['asientos'][asiento_actual]
        contador = 1 if asiento['estado'] == 'disponible' else 0
        
        # Recursión al siguiente asiento
        return contador + self.contar_asientos_disponibles_recursivo(
            sala_tree, fila_actual, asiento_actual + 1
        )
    
    def generar_qr_recursivo(self, datos: str, intento: int = 1, max_intentos: int = 3) -> Any:
        """
        Generar QR con reintentos recursivos si falla
        Complejidad: O(1) por intento
        """
        if intento > max_intentos:
            raise Exception("No se pudo generar QR después de 3 intentos")
        
        try:
            qr = qrcode.QRCode(version=intento, box_size=10, border=5)
            qr.add_data(datos)
            qr.make(fit=True)
            return qr.make_image(fill_color="black", back_color="white")
        except Exception:
            # Reintento recursivo con versión diferente
            return self.generar_qr_recursivo(datos, intento + 1, max_intentos)
    
    def calcular_factorial_recursivo(self, n: int) -> int:
        """
        Calcular factorial de forma recursiva
        Usado para cálculos de probabilidad en recomendaciones
        """
        if n <= 1:
            return 1
        return n * self.calcular_factorial_recursivo(n - 1)
    
    def fibonacci_recursivo(self, n: int) -> int:
        """
        Secuencia de Fibonacci recursiva
        Usado para algoritmos de distribución de asientos
        """
        if n <= 1:
            return n
        return self.fibonacci_recursivo(n - 1) + self.fibonacci_recursivo(n - 2)
    
    # ==================== MÉTODOS DE ORDENAMIENTO ====================
    
    def quicksort_peliculas_rating(self, peliculas: List[Dict], inicio: int = 0, fin: Optional[int] = None) -> List[Dict]:
        """
        Ordenar películas por rating usando QuickSort
        Complejidad: O(n log n) promedio, O(n²) peor caso
        """
        if fin is None:
            fin = len(peliculas) - 1
        
        if inicio < fin:
            # Particionar y obtener índice del pivote
            pivote_idx = self._particionar_por_rating(peliculas, inicio, fin)
            
            # Ordenar recursivamente las dos mitades
            self.quicksort_peliculas_rating(peliculas, inicio, pivote_idx - 1)
            self.quicksort_peliculas_rating(peliculas, pivote_idx + 1, fin)
        
        return peliculas
    
    def _particionar_por_rating(self, peliculas: List[Dict], inicio: int, fin: int) -> int:
        """
        Función auxiliar para QuickSort
        """
        pivote = peliculas[fin].get('rating', 0)
        i = inicio - 1
        
        for j in range(inicio, fin):
            if peliculas[j].get('rating', 0) >= pivote:  # Orden descendente
                i += 1
                peliculas[i], peliculas[j] = peliculas[j], peliculas[i]
        
        peliculas[i + 1], peliculas[fin] = peliculas[fin], peliculas[i + 1]
        return i + 1
    
    def mergesort_funciones_hora(self, funciones: List[Dict]) -> List[Dict]:
        """
        Ordenar funciones por hora usando MergeSort
        Complejidad: O(n log n) siempre
        """
        if len(funciones) <= 1:
            return funciones
        
        # Dividir en dos mitades
        medio = len(funciones) // 2
        izquierda = self.mergesort_funciones_hora(funciones[:medio])
        derecha = self.mergesort_funciones_hora(funciones[medio:])
        
        # Combinar las dos mitades ordenadas
        return self._combinar_funciones(izquierda, derecha)
    
    def _combinar_funciones(self, izquierda: List[Dict], derecha: List[Dict]) -> List[Dict]:
        """
        Combinar dos listas ordenadas de funciones
        """
        resultado = []
        i = j = 0
        
        while i < len(izquierda) and j < len(derecha):
            if izquierda[i].get('hora', '') <= derecha[j].get('hora', ''):
                resultado.append(izquierda[i])
                i += 1
            else:
                resultado.append(derecha[j])
                j += 1
        
        # Agregar elementos restantes
        resultado.extend(izquierda[i:])
        resultado.extend(derecha[j:])
        
        return resultado
    
    def heapsort_transacciones_fecha(self, transacciones: List[Dict]) -> List[Dict]:
        """
        Ordenar transacciones por fecha usando HeapSort
        Complejidad: O(n log n) siempre
        """
        n = len(transacciones)
        
        # Construir heap máximo
        for i in range(n // 2 - 1, -1, -1):
            self._heapify_transacciones(transacciones, n, i)
        
        # Extraer elementos del heap uno por uno
        for i in range(n - 1, 0, -1):
            transacciones[0], transacciones[i] = transacciones[i], transacciones[0]
            self._heapify_transacciones(transacciones, i, 0)
        
        return transacciones
    
    def _heapify_transacciones(self, transacciones: List[Dict], n: int, i: int):
        """
        Heapify para transacciones
        """
        mayor = i
        izquierda = 2 * i + 1
        derecha = 2 * i + 2
        
        if (izquierda < n and 
            transacciones[izquierda].get('fecha_transaccion', '') > 
            transacciones[mayor].get('fecha_transaccion', '')):
            mayor = izquierda
        
        if (derecha < n and 
            transacciones[derecha].get('fecha_transaccion', '') > 
            transacciones[mayor].get('fecha_transaccion', '')):
            mayor = derecha
        
        if mayor != i:
            transacciones[i], transacciones[mayor] = transacciones[mayor], transacciones[i]
            self._heapify_transacciones(transacciones, n, mayor)
    
    # ==================== MÉTODOS DE BÚSQUEDA ====================
    
    def busqueda_binaria_peliculas(self, peliculas_ordenadas: List[Dict], titulo_buscar: str) -> Optional[Dict]:
        """
        Búsqueda binaria en películas ordenadas por título
        Complejidad: O(log n)
        """
        izquierda, derecha = 0, len(peliculas_ordenadas) - 1
        
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            pelicula_medio = peliculas_ordenadas[medio].get('titulo', '')
            
            if pelicula_medio == titulo_buscar:
                return peliculas_ordenadas[medio]
            elif pelicula_medio < titulo_buscar:
                izquierda = medio + 1
            else:
                derecha = medio - 1
        
        return None
    
    def busqueda_lineal_filtros(self, peliculas: List[Dict], filtros: Dict[str, Any]) -> List[Dict]:
        """
        Búsqueda lineal con múltiples criterios
        Complejidad: O(n * m) donde n=películas, m=criterios
        """
        resultados = []
        
        for pelicula in peliculas:
            coincide = True
            
            for criterio, valor in filtros.items():
                if criterio == 'genero':
                    if valor not in pelicula.get('generos', []):
                        coincide = False
                        break
                elif criterio == 'duracion_max':
                    if pelicula.get('duracion_minutos', 0) > valor:
                        coincide = False
                        break
                elif criterio == 'precio_max':
                    if pelicula.get('precio_base', 0) > valor:
                        coincide = False
                        break
                elif criterio == 'activa':
                    if pelicula.get('activa', False) != valor:
                        coincide = False
                        break
                elif criterio == 'director':
                    if valor.lower() not in pelicula.get('director', '').lower():
                        coincide = False
                        break
            
            if coincide:
                resultados.append(pelicula)
        
        return resultados
    
    def dfs_recomendaciones(self, grafo_usuario: Dict, usuario_id: str, profundidad_max: int = 3, visitados: Optional[Set] = None) -> List[str]:
        """
        Búsqueda en profundidad para encontrar películas recomendadas
        Complejidad: O(V + E) donde V=vertices, E=edges
        """
        if visitados is None:
            visitados = set()
        
        if profundidad_max == 0 or usuario_id in visitados:
            return []
        
        visitados.add(usuario_id)
        recomendaciones = []
        
        # Buscar conexiones del usuario
        for edge in grafo_usuario.get('edges', []):
            if edge['from'] == usuario_id and edge['relation'] == 'watched':
                pelicula_id = edge['to']
                
                # Buscar películas similares
                for edge_similar in grafo_usuario.get('edges', []):
                    if (edge_similar['from'] == pelicula_id and 
                        edge_similar['relation'] == 'similar_genre'):
                        recomendaciones.append(edge_similar['to'])
                
                # Recursión para profundidad
                sub_recomendaciones = self.dfs_recomendaciones(
                    grafo_usuario, 
                    pelicula_id, 
                    profundidad_max - 1, 
                    visitados.copy()
                )
                recomendaciones.extend(sub_recomendaciones)
        
        return list(set(recomendaciones))  # Eliminar duplicados
    
    def bfs_asientos_cercanos(self, sala_tree: Dict, asiento_inicial: str, distancia_max: int = 3) -> List[str]:
        """
        Búsqueda en anchura para encontrar asientos cercanos disponibles
        Complejidad: O(V + E) donde V=asientos, E=conexiones
        """
        from collections import deque
        
        cola = deque([(asiento_inicial, 0)])  # (asiento, distancia)
        visitados = set()
        asientos_cercanos = []
        
        while cola:
            asiento_actual, distancia = cola.popleft()
            
            if asiento_actual in visitados or distancia > distancia_max:
                continue
            
            visitados.add(asiento_actual)
            
            # Verificar si el asiento está disponible
            if self._es_asiento_disponible(sala_tree, asiento_actual):
                asientos_cercanos.append(asiento_actual)
            
            # Agregar asientos adyacentes
            for asiento_vecino in self._obtener_asientos_vecinos(sala_tree, asiento_actual):
                if asiento_vecino not in visitados:
                    cola.append((asiento_vecino, distancia + 1))
        
        return asientos_cercanos
    
    def _es_asiento_disponible(self, sala_tree: Dict, asiento_id: str) -> bool:
        """Verificar si un asiento está disponible"""
        for fila in sala_tree.get('filas', []):
            for asiento in fila.get('asientos', []):
                if asiento.get('numero') == asiento_id:
                    return asiento.get('estado') == 'disponible'
        return False
    
    def _obtener_asientos_vecinos(self, sala_tree: Dict, asiento_id: str) -> List[str]:
        """Obtener asientos adyacentes"""
        # Implementación simplificada - en realidad dependería de la disposición de la sala
        fila = asiento_id[0]
        numero = int(asiento_id[1:])
        
        vecinos = []
        for offset in [-1, 1]:
            nuevo_numero = numero + offset
            if 1 <= nuevo_numero <= 20:  # Asumiendo máximo 20 asientos por fila
                vecinos.append(f"{fila}{nuevo_numero}")
        
        return vecinos
    
    # ==================== MÉTODOS DE OPTIMIZACIÓN ====================
    
    def optimizar_cache_peliculas(self, peliculas: List[Dict]) -> Dict[str, Dict]:
        """
        Crear índice hash para búsqueda rápida de películas
        Complejidad: O(n) para construcción, O(1) para búsqueda
        """
        cache = {}
        for pelicula in peliculas:
            # Índice por ID
            cache[pelicula.get('_id', '')] = pelicula
            # Índice por título
            cache[pelicula.get('titulo', '').lower()] = pelicula
            # Índice por director
            director = pelicula.get('director', '').lower()
            if director not in cache:
                cache[director] = []
            cache[director].append(pelicula)
        
        return cache
    
    def calcular_complejidad_algoritmo(self, algoritmo: str, n: int) -> Dict[str, Any]:
        """
        Calcular complejidad temporal y espacial de algoritmos
        """
        complejidades = {
            'quicksort': {'temporal': 'O(n log n)', 'espacial': 'O(log n)'},
            'mergesort': {'temporal': 'O(n log n)', 'espacial': 'O(n)'},
            'heapsort': {'temporal': 'O(n log n)', 'espacial': 'O(1)'},
            'busqueda_binaria': {'temporal': 'O(log n)', 'espacial': 'O(1)'},
            'busqueda_lineal': {'temporal': 'O(n)', 'espacial': 'O(1)'},
            'dfs': {'temporal': 'O(V + E)', 'espacial': 'O(V)'},
            'bfs': {'temporal': 'O(V + E)', 'espacial': 'O(V)'}
        }
        
        return {
            'algoritmo': algoritmo,
            'complejidad_temporal': complejidades.get(algoritmo, {}).get('temporal', 'O(1)'),
            'complejidad_espacial': complejidades.get(algoritmo, {}).get('espacial', 'O(1)'),
            'tamaño_entrada': n
        }
    
    def benchmark_algoritmo(self, algoritmo: str, datos: List[Dict]) -> Dict[str, Any]:
        """
        Medir rendimiento de algoritmos
        """
        import time
        
        inicio = time.time()
        
        if algoritmo == 'quicksort':
            resultado = self.quicksort_peliculas_rating(datos.copy())
        elif algoritmo == 'mergesort':
            resultado = self.mergesort_funciones_hora(datos.copy())
        elif algoritmo == 'busqueda_lineal':
            resultado = self.busqueda_lineal_filtros(datos, {'activa': True})
        else:
            resultado = datos
        
        fin = time.time()
        
        return {
            'algoritmo': algoritmo,
            'tiempo_ejecucion': fin - inicio,
            'tamaño_datos': len(datos),
            'resultado_tamaño': len(resultado) if isinstance(resultado, list) else 1
        }


# Instancia global del servicio
algorithms_service = AlgorithmsService() 