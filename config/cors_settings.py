from typing import List

# Configuración de CORS
CORS_ORIGINS: List[str] = [
    # Frontend en producción
    "https://upcfronted.netlify.app",
    "https://upcfronted.netlify.app/",
    
    # Túneles de Cloudflare
    "https://moms-geographic-serial-forget.trycloudflare.com",
    "https://*.trycloudflare.com",
    "https://*.cloudflareaccess.com",
    
    # Desarrollo local
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:8080",
    "http://localhost:4173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:4173",
    
    # Otros dominios de desarrollo
    "http://localhost:*",
    "https://localhost:*",
]

CORS_METHODS: List[str] = [
    "GET",
    "POST", 
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH"
]

CORS_HEADERS: List[str] = [
    "Accept",
    "Accept-Language", 
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Origin",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers"
] 