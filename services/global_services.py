"""
Servicios globales para evitar import circular
"""

# Servicios globales - Inicializar como None por ahora
redis_service = None
mongodb_service = None
algorithms_service = None

def set_redis_service(service):
    """Establece el servicio de Redis"""
    global redis_service
    redis_service = service

def set_mongodb_service(service):
    """Establece el servicio de MongoDB"""
    global mongodb_service
    mongodb_service = service

def set_algorithms_service(service):
    """Establece el servicio de algoritmos"""
    global algorithms_service
    algorithms_service = service

def get_redis_service():
    """Obtiene el servicio de Redis"""
    return redis_service

def get_mongodb_service():
    """Obtiene el servicio de MongoDB"""
    return mongodb_service

def get_algorithms_service():
    """Obtiene el servicio de algoritmos"""
    return algorithms_service 