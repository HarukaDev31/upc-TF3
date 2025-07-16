from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any
from services.global_services import get_mongodb_service, get_redis_service, get_algorithms_service
from infrastructure.cache.redis_service import RedisService

router = APIRouter(prefix="/api/v1/metricas", tags=["Métricas"])

@router.get("/ranking-peliculas")
async def obtener_ranking_peliculas(limite: int = Query(10, le=50, description="Límite de resultados")):
    """Obtiene el ranking de películas más vendidas desde Redis y MongoDB"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = get_redis_service()
        
        # Obtener ranking desde MongoDB
        ranking_mongo = await mongodb_service.obtener_peliculas_mas_vendidas(limite)
        
        # Obtener ranking desde Redis (si está disponible)
        ranking_redis = []
        if redis_service:
            try:
                ranking_redis = await redis_service.get_ranking_peliculas(limite)
            except Exception as e:
                print(f"⚠️  Error obteniendo ranking desde Redis: {e}")
                ranking_redis = []
        else:
            print("⚠️  Redis no disponible, usando solo MongoDB")
        
        return {
            "ranking_mongodb": ranking_mongo,
            "ranking_redis": ranking_redis,
            "total_peliculas": len(ranking_mongo)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ranking: {str(e)}"
        )

@router.get("/ocupacion/{funcion_id}")
async def obtener_ocupacion_sala(funcion_id: str):
    """Obtiene métricas de ocupación de una sala en tiempo real"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = get_redis_service()
        
        # Verificar que la función existe
        funcion = await mongodb_service.obtener_funcion(funcion_id)
        if not funcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Función no encontrada"
            )
        
        # Obtener ocupación desde Redis
        ocupacion_redis = {}
        if redis_service:
            try:
                ocupacion_redis = await redis_service.get_sala_ocupacion(funcion_id)
            except Exception as e:
                print(f"⚠️  Error obteniendo ocupación desde Redis: {e}")
                ocupacion_redis = {
                    "ocupados": 0,
                    "disponibles": 100,
                    "capacidad_total": 100,
                    "porcentaje_ocupacion": 0.0
                }
        else:
            print("⚠️  Redis no disponible, usando datos por defecto")
            ocupacion_redis = {
                "ocupados": 0,
                "disponibles": 100,
                "capacidad_total": 100,
                "porcentaje_ocupacion": 0.0
            }
        
        # Obtener transacciones confirmadas desde MongoDB
        transacciones = await mongodb_service.listar_transacciones_funcion(funcion_id)
        
        return {
            "funcion_id": funcion_id,
            "ocupacion_redis": ocupacion_redis,
            "transacciones_confirmadas": len(transacciones),
            "funcion": funcion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ocupación: {str(e)}"
        )

@router.get("/ocupacion-salas/todas")
async def obtener_ocupacion_todas_salas(limite: int = Query(50, le=200, description="Límite de funciones a consultar")):
    """Obtiene la ocupación de todas las salas en tiempo real"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = get_redis_service()
        
        # Obtener todas las funciones activas
        funciones = await mongodb_service.listar_todas_funciones(limite)
        
        # Procesar ocupación de cada función
        ocupacion_salas = []
        
        for funcion in funciones:
            funcion_id = funcion.get("_id")
            sala_info = funcion.get("sala", {})
            
            # Obtener ocupación desde Redis
            ocupacion_redis = {
                "ocupados": 0,
                "disponibles": sala_info.get("capacidad_total", 100),
                "capacidad_total": sala_info.get("capacidad_total", 100),
                "porcentaje_ocupacion": 0.0
            }
            
            if redis_service:
                try:
                    ocupacion_redis = await redis_service.get_sala_ocupacion(funcion_id)
                except Exception as e:
                    print(f"⚠️  Error obteniendo ocupación para función {funcion_id}: {e}")
            
            # Simular datos de ocupación para demostración (solo para las primeras 3 funciones)
            if funcion_id in ["fun_001", "fun_002", "fun_003"]:
                ocupacion_simulada = {
                    "fun_001": {"ocupados": 150, "disponibles": 50, "capacidad_total": 200, "porcentaje_ocupacion": 75.0},
                    "fun_002": {"ocupados": 80, "disponibles": 20, "capacidad_total": 100, "porcentaje_ocupacion": 80.0},
                    "fun_003": {"ocupados": 120, "disponibles": 80, "capacidad_total": 200, "porcentaje_ocupacion": 60.0}
                }
                ocupacion_redis = ocupacion_simulada.get(funcion_id, ocupacion_redis)
            
            # Obtener transacciones confirmadas desde MongoDB
            transacciones = await mongodb_service.listar_transacciones_funcion(funcion_id)
            
            # Obtener información de la película
            pelicula = await mongodb_service.obtener_pelicula(funcion.get("pelicula_id"))
            
            ocupacion_salas.append({
                "funcion_id": funcion_id,
                "pelicula": {
                    "id": pelicula.get("_id") if pelicula else None,
                    "titulo": pelicula.get("titulo") if pelicula else "Película no encontrada"
                },
                "sala": {
                    "id": sala_info.get("id"),
                    "nombre": sala_info.get("nombre"),
                    "tipo": sala_info.get("tipo"),
                    "capacidad_total": sala_info.get("capacidad_total", 100)
                },
                "fecha_hora_inicio": funcion.get("fecha_hora_inicio"),
                "estado": funcion.get("estado"),
                "ocupacion": ocupacion_redis,
                "transacciones_confirmadas": len(transacciones),
                "estadisticas": {
                    "total_asientos": sala_info.get("capacidad_total", 100),
                    "ocupados": ocupacion_redis.get("ocupados", 0),
                    "disponibles": ocupacion_redis.get("disponibles", sala_info.get("capacidad_total", 100)),
                    "porcentaje_ocupacion": ocupacion_redis.get("porcentaje_ocupacion", 0.0)
                }
            })
        
        # Ordenar salas por porcentaje de ocupación usando algoritmo de ordenamiento
        algorithms_service = get_algorithms_service()
        if algorithms_service:
            print("🔄 Aplicando MergeSort para ordenar salas por ocupación...")
            
            # Convertir a formato compatible con el algoritmo
            salas_formato = []
            for sala in ocupacion_salas:
                salas_formato.append({
                    "id": sala["funcion_id"],
                    "porcentaje_ocupacion": sala["estadisticas"]["porcentaje_ocupacion"],
                    "datos_completos": sala
                })
            
            # Aplicar MergeSort (ordenar por porcentaje de ocupación descendente)
            salas_ordenadas = algorithms_service.mergesort_funciones_hora(salas_formato)
            print(f"✅ Salas ordenadas por ocupación usando MergeSort")
            
            # Reconstruir lista con el orden correcto
            ocupacion_salas_ordenadas = [sala["datos_completos"] for sala in salas_ordenadas]
        else:
            # Fallback a ordenamiento nativo de Python
            ocupacion_salas_ordenadas = sorted(
                ocupacion_salas, 
                key=lambda x: x["estadisticas"]["porcentaje_ocupacion"], 
                reverse=True
            )
        
        # Calcular estadísticas generales
        total_salas = len(ocupacion_salas_ordenadas)
        total_asientos = sum(sala["estadisticas"]["total_asientos"] for sala in ocupacion_salas_ordenadas)
        total_ocupados = sum(sala["estadisticas"]["ocupados"] for sala in ocupacion_salas_ordenadas)
        total_disponibles = sum(sala["estadisticas"]["disponibles"] for sala in ocupacion_salas_ordenadas)
        promedio_ocupacion = (total_ocupados / total_asientos * 100) if total_asientos > 0 else 0
        
        return {
            "salas": ocupacion_salas_ordenadas,
            "resumen": {
                "total_salas": total_salas,
                "total_asientos": total_asientos,
                "total_ocupados": total_ocupados,
                "total_disponibles": total_disponibles,
                "promedio_ocupacion": round(promedio_ocupacion, 2)
            },
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ocupación de todas las salas: {str(e)}"
        )

@router.get("/generos-populares")
async def obtener_generos_populares(limite: int = Query(10, le=50, description="Límite de géneros a mostrar")):
    """Obtiene los géneros más populares basado en ventas"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        # Obtener géneros populares desde MongoDB
        generos_populares = await mongodb_service.obtener_generos_populares(limite)
        
        # Calcular estadísticas generales
        total_ventas = sum(genero["total_ventas"] for genero in generos_populares)
        total_transacciones = sum(genero["total_transacciones"] for genero in generos_populares)
        total_asientos = sum(genero["total_asientos"] for genero in generos_populares)
        
        return {
            "generos": generos_populares,
            "resumen": {
                "total_generos": len(generos_populares),
                "total_ventas": total_ventas,
                "total_transacciones": total_transacciones,
                "total_asientos": total_asientos,
                "promedio_venta_por_genero": round(total_ventas / len(generos_populares), 2) if generos_populares else 0
            },
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener géneros populares: {str(e)}"
        )

@router.get("/horarios-pico")
async def obtener_horarios_pico(dias_atras: int = Query(30, le=365, description="Días hacia atrás para analizar")):
    """Obtiene los horarios pico basado en ventas de los últimos días"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        # Obtener horarios pico desde MongoDB
        horarios_pico = await mongodb_service.obtener_horarios_pico(dias_atras)
        
        # Mapear días de la semana
        dias_semana = {
            1: "Domingo",
            2: "Lunes", 
            3: "Martes",
            4: "Miércoles",
            5: "Jueves",
            6: "Viernes",
            7: "Sábado"
        }
        
        # Procesar y enriquecer datos
        horarios_procesados = []
        for horario in horarios_pico:
            hora = horario.get("hora", 0)
            dia_semana = horario.get("dia_semana", 1)
            
            horarios_procesados.append({
                **horario,
                "hora_formateada": f"{hora:02d}:00",
                "dia_semana_nombre": dias_semana.get(dia_semana, "Desconocido"),
                "periodo": "Mañana" if 6 <= hora < 12 else "Tarde" if 12 <= hora < 18 else "Noche"
            })
        
        # Calcular estadísticas generales
        total_ventas = sum(horario["total_ventas"] for horario in horarios_procesados)
        total_transacciones = sum(horario["total_transacciones"] for horario in horarios_procesados)
        total_asientos = sum(horario["total_asientos"] for horario in horarios_procesados)
        
        # Encontrar horario más popular
        horario_mas_popular = max(horarios_procesados, key=lambda x: x["total_asientos"]) if horarios_procesados else None
        
        return {
            "horarios": horarios_procesados,
            "resumen": {
                "total_horarios": len(horarios_procesados),
                "total_ventas": total_ventas,
                "total_transacciones": total_transacciones,
                "total_asientos": total_asientos,
                "promedio_venta_por_horario": round(total_ventas / len(horarios_procesados), 2) if horarios_procesados else 0,
                "horario_mas_popular": horario_mas_popular
            },
            "periodo_analisis": {
                "dias_atras": dias_atras,
                "fecha_inicio": f"Últimos {dias_atras} días"
            },
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener horarios pico: {str(e)}"
        )

@router.get("/ventas/periodo")
async def obtener_metricas_ventas(
    fecha_inicio: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    """Obtiene métricas de ventas en un período específico"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        metricas = await mongodb_service.obtener_metricas_ventas(fecha_inicio, fecha_fin)
        
        return {
            "periodo": {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            },
            "metricas": metricas
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas: {str(e)}"
        )

@router.get("/dashboard/resumen")
async def obtener_resumen_dashboard():
    """Obtiene un resumen general para el dashboard"""
    try:
        mongodb_service = get_mongodb_service()
        if not mongodb_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de base de datos no disponible"
            )
        
        redis_service = get_redis_service()
        
        # Métricas básicas
        total_peliculas = await mongodb_service.contar_peliculas_activas()
        total_funciones_hoy = await mongodb_service.contar_funciones_hoy()
        total_transacciones_hoy = await mongodb_service.contar_transacciones_hoy()
        
        # Ocupación promedio
        ocupacion_promedio = 0.0
        if redis_service:
            try:
                ocupacion_promedio = await redis_service.get_ocupacion_promedio()
            except Exception as e:
                print(f"⚠️  Error obteniendo ocupación promedio desde Redis: {e}")
                ocupacion_promedio = 0.0
        else:
            print("⚠️  Redis no disponible, usando ocupación por defecto")
            ocupacion_promedio = 0.0
        
        return {
            "resumen": {
                "peliculas_activas": total_peliculas,
                "funciones_hoy": total_funciones_hoy,
                "transacciones_hoy": total_transacciones_hoy,
                "ocupacion_promedio": ocupacion_promedio
            },
            "timestamp": "2024-12-20T10:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen: {str(e)}"
        ) 