from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    mongodb_url: str = "mongodb://admin:password123@localhost:27017/cinemax?authSource=admin"
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
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
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
    
    # Email Configuration
    smtp_host: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="tu-email@gmail.com", validation_alias="SMTP_USER")
    smtp_password: str = Field(default="tu-password", validation_alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, validation_alias="SMTP_USE_TLS")
    smtp_verify_ssl: bool = Field(default=True, validation_alias="SMTP_VERIFY_SSL")
    smtp_max_retries: int = Field(default=3, validation_alias="SMTP_MAX_RETRIES")
    smtp_timeout: int = Field(default=30, validation_alias="SMTP_TIMEOUT")
    
    # Email Templates
    email_from_name: str = Field(default="Cinemax", validation_alias="EMAIL_FROM_NAME")
    email_from_address: str = Field(default="noreply@cinemax.com", validation_alias="EMAIL_FROM_ADDRESS")
    email_reply_to: str = Field(default="support@cinemax.com", validation_alias="EMAIL_REPLY_TO")
    
    # Email Features
    enable_email_notifications: bool = Field(default=True, validation_alias="ENABLE_EMAIL_NOTIFICATIONS")
    email_batch_size: int = Field(default=10, validation_alias="EMAIL_BATCH_SIZE")
    email_retry_delay: int = Field(default=5, validation_alias="EMAIL_RETRY_DELAY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 