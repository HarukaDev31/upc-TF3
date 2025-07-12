from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    mongodb_url: str = "mongodb://admin:password123@localhost:27017"
    mongodb_database: str = "cinemax"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6380  # Cambiado para evitar conflicto con Redis local
    redis_password: Optional[str] = None
    redis_db: int = 0
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_socket_keepalive: bool = True
    redis_socket_keepalive_options: dict = {}
    
    # Application Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "Sistema de Cine"
    secret_key: str = "tu-clave-secreta-muy-segura-aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # External Services
    payment_gateway_url: str = "https://api.payment-provider.com"
    payment_gateway_api_key: str = "tu-api-key-del-gateway"
    
    # Metrics
    enable_metrics: bool = True
    metrics_port: int = 8000
    
    # Performance
    redis_pool_max_connections: int = 50
    mongodb_max_connections: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 