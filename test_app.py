from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Test API",
    description="API de prueba sin dependencias",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "mensaje": "🎬 Test API - Funcionando!",
        "version": "1.0.0",
        "estado": "activo"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "estado": "saludable",
        "servicios": {
            "api": "conectado"
        }
    }

@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba"""
    return {
        "mensaje": "¡Endpoint funcionando correctamente!",
        "data": {
            "test": True,
            "timestamp": "2024-12-20T10:00:00Z"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "test_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 