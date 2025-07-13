"""
Servicios globales para evitar import circular
"""

# Servicios globales - Inicializar como None por ahora
redis_service = None
mongodb_service = None

def set_redis_service(service):
    """Establece el servicio de Redis"""
    global redis_service
    redis_service = service

def set_mongodb_service(service):
    """Establece el servicio de MongoDB"""
    global mongodb_service
    mongodb_service = service

def get_redis_service():
    """Obtiene el servicio de Redis"""
    return redis_service

def get_mongodb_service():
    """Obtiene el servicio de MongoDB"""
    return mongodb_service 