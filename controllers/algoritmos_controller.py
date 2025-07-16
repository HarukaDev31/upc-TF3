"""
Controlador para algoritmos de estructuras de datos
Expone métodos recursivos, ordenamiento y búsqueda
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from services.algorithms_service import algorithms_service
from controllers.usuarios_controller import get_current_user

router = APIRouter(prefix="/api/v1/algoritmos", tags=["Algoritmos"])


class FiltrosBusqueda(BaseModel):
    genero: Optional[str] = None
    duracion_max: Optional[int] = None
    precio_max: Optional[int] = None
    activa: Optional[bool] = None
    director: Optional[str] = None


class DatosAlgoritmo(BaseModel):
    algoritmo: str
    datos: List[Dict[str, Any]]


@router.post("/recursivos/buscar-genero")
async def buscar_genero_recursivo(
    arbol_generos: List[Dict],
    genero_buscar: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Búsqueda recursiva en árbol de géneros
    """
    try:
        resultado = algorithms_service.buscar_genero_recursivo(arbol_generos, genero_buscar)
        return {
            "success": True,
            "resultado": resultado,
            "algoritmo": "búsqueda_recursiva_arbol",
            "complejidad": "O(n)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recursivos/contar-asientos")
async def contar_asientos_recursivo(
    sala_tree: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """
    Contar asientos disponibles de forma recursiva
    """
    try:
        total_disponibles = algorithms_service.contar_asientos_disponibles_recursivo(sala_tree)
        return {
            "success": True,
            "total_disponibles": total_disponibles,
            "algoritmo": "recursión_asientos",
            "complejidad": "O(n*m)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recursivos/generar-qr")
async def generar_qr_recursivo(
    datos: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generar QR con reintentos recursivos
    """
    try:
        qr_image = algorithms_service.generar_qr_recursivo(datos)
        # Convertir imagen a base64 para respuesta
        import base64
        import io
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return {
            "success": True,
            "qr_base64": img_str,
            "algoritmo": "generación_qr_recursiva",
            "complejidad": "O(1) por intento"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recursivos/factorial")
async def calcular_factorial_recursivo(
    n: int,
    current_user: Dict = Depends(get_current_user)
):
    """
    Calcular factorial de forma recursiva
    """
    try:
        if n > 20:  # Limitar para evitar stack overflow
            raise HTTPException(status_code=400, detail="Número demasiado grande")
        
        resultado = algorithms_service.calcular_factorial_recursivo(n)
        return {
            "success": True,
            "n": n,
            "factorial": resultado,
            "algoritmo": "factorial_recursivo",
            "complejidad": "O(n)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recursivos/fibonacci")
async def fibonacci_recursivo(
    n: int,
    current_user: Dict = Depends(get_current_user)
):
    """
    Secuencia de Fibonacci recursiva
    """
    try:
        if n > 30:  # Limitar para evitar stack overflow
            raise HTTPException(status_code=400, detail="Número demasiado grande")
        
        resultado = algorithms_service.fibonacci_recursivo(n)
        return {
            "success": True,
            "n": n,
            "fibonacci": resultado,
            "algoritmo": "fibonacci_recursivo",
            "complejidad": "O(2^n)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ordenamiento/quicksort-peliculas")
async def quicksort_peliculas(
    peliculas: List[Dict],
    current_user: Dict = Depends(get_current_user)
):
    """
    Ordenar películas por rating usando QuickSort
    """
    try:
        peliculas_ordenadas = algorithms_service.quicksort_peliculas_rating(peliculas.copy())
        return {
            "success": True,
            "peliculas_ordenadas": peliculas_ordenadas,
            "algoritmo": "quicksort",
            "complejidad": "O(n log n) promedio"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ordenamiento/mergesort-funciones")
async def mergesort_funciones(
    funciones: List[Dict],
    current_user: Dict = Depends(get_current_user)
):
    """
    Ordenar funciones por hora usando MergeSort
    """
    try:
        funciones_ordenadas = algorithms_service.mergesort_funciones_hora(funciones.copy())
        return {
            "success": True,
            "funciones_ordenadas": funciones_ordenadas,
            "algoritmo": "mergesort",
            "complejidad": "O(n log n)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ordenamiento/heapsort-transacciones")
async def heapsort_transacciones(
    transacciones: List[Dict],
    current_user: Dict = Depends(get_current_user)
):
    """
    Ordenar transacciones por fecha usando HeapSort
    """
    try:
        transacciones_ordenadas = algorithms_service.heapsort_transacciones_fecha(transacciones.copy())
        return {
            "success": True,
            "transacciones_ordenadas": transacciones_ordenadas,
            "algoritmo": "heapsort",
            "complejidad": "O(n log n)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/busqueda/binaria-peliculas")
async def busqueda_binaria_peliculas(
    peliculas_ordenadas: List[Dict],
    titulo_buscar: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Búsqueda binaria en películas ordenadas por título
    """
    try:
        resultado = algorithms_service.busqueda_binaria_peliculas(peliculas_ordenadas, titulo_buscar)
        return {
            "success": True,
            "pelicula_encontrada": resultado,
            "algoritmo": "búsqueda_binaria",
            "complejidad": "O(log n)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/busqueda/lineal-filtros")
async def busqueda_lineal_filtros(
    peliculas: List[Dict],
    filtros: FiltrosBusqueda,
    current_user: Dict = Depends(get_current_user)
):
    """
    Búsqueda lineal con múltiples criterios
    """
    try:
        filtros_dict = filtros.dict(exclude_none=True)
        resultados = algorithms_service.busqueda_lineal_filtros(peliculas, filtros_dict)
        return {
            "success": True,
            "peliculas_encontradas": resultados,
            "total_resultados": len(resultados),
            "filtros_aplicados": filtros_dict,
            "algoritmo": "búsqueda_lineal",
            "complejidad": "O(n * m)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/busqueda/dfs-recomendaciones")
async def dfs_recomendaciones(
    grafo_usuario: Dict,
    usuario_id: str,
    profundidad_max: int = 3,
    current_user: Dict = Depends(get_current_user)
):
    """
    Búsqueda en profundidad para encontrar películas recomendadas
    """
    try:
        recomendaciones = algorithms_service.dfs_recomendaciones(
            grafo_usuario, usuario_id, profundidad_max
        )
        return {
            "success": True,
            "recomendaciones": recomendaciones,
            "total_recomendaciones": len(recomendaciones),
            "profundidad_max": profundidad_max,
            "algoritmo": "dfs",
            "complejidad": "O(V + E)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/busqueda/bfs-asientos")
async def bfs_asientos_cercanos(
    sala_tree: Dict,
    asiento_inicial: str,
    distancia_max: int = 3,
    current_user: Dict = Depends(get_current_user)
):
    """
    Búsqueda en anchura para encontrar asientos cercanos disponibles
    """
    try:
        asientos_cercanos = algorithms_service.bfs_asientos_cercanos(
            sala_tree, asiento_inicial, distancia_max
        )
        return {
            "success": True,
            "asientos_cercanos": asientos_cercanos,
            "total_asientos": len(asientos_cercanos),
            "asiento_inicial": asiento_inicial,
            "distancia_max": distancia_max,
            "algoritmo": "bfs",
            "complejidad": "O(V + E)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimizacion/cache-peliculas")
async def optimizar_cache_peliculas(
    peliculas: List[Dict],
    current_user: Dict = Depends(get_current_user)
):
    """
    Crear índice hash para búsqueda rápida de películas
    """
    try:
        cache_optimizado = algorithms_service.optimizar_cache_peliculas(peliculas)
        return {
            "success": True,
            "cache_optimizado": cache_optimizado,
            "total_indices": len(cache_optimizado),
            "algoritmo": "hash_indexing",
            "complejidad": "O(n) construcción, O(1) búsqueda"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analisis/complejidad")
async def calcular_complejidad(
    algoritmo: str,
    n: int,
    current_user: Dict = Depends(get_current_user)
):
    """
    Calcular complejidad temporal y espacial de algoritmos
    """
    try:
        complejidad = algorithms_service.calcular_complejidad_algoritmo(algoritmo, n)
        return {
            "success": True,
            "analisis_complejidad": complejidad
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark/rendimiento")
async def benchmark_algoritmo(
    datos_algoritmo: DatosAlgoritmo,
    current_user: Dict = Depends(get_current_user)
):
    """
    Medir rendimiento de algoritmos
    """
    try:
        benchmark = algorithms_service.benchmark_algoritmo(
            datos_algoritmo.algoritmo, 
            datos_algoritmo.datos
        )
        return {
            "success": True,
            "benchmark": benchmark
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def info_algoritmos():
    """
    Información sobre algoritmos disponibles
    """
    return {
        "success": True,
        "algoritmos_disponibles": {
            "recursivos": [
                "buscar_genero_recursivo",
                "contar_asientos_disponibles_recursivo", 
                "generar_qr_recursivo",
                "calcular_factorial_recursivo",
                "fibonacci_recursivo"
            ],
            "ordenamiento": [
                "quicksort_peliculas_rating",
                "mergesort_funciones_hora",
                "heapsort_transacciones_fecha"
            ],
            "busqueda": [
                "busqueda_binaria_peliculas",
                "busqueda_lineal_filtros",
                "dfs_recomendaciones",
                "bfs_asientos_cercanos"
            ],
            "optimizacion": [
                "optimizar_cache_peliculas",
                "calcular_complejidad_algoritmo",
                "benchmark_algoritmo"
            ]
        },
        "estructuras_datos": [
            "Pilas (Stacks) - Redis",
            "Colas (Queues) - Redis", 
            "Listas Enlazadas - MongoDB",
            "Tablas Hash - Redis",
            "Árboles - MongoDB",
            "Grafos - MongoDB"
        ]
    } 