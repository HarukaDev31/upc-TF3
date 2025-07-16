# Script para iniciar túnel de API (puerto 8000)
Write-Host "🚀 Iniciando túnel para API Principal (puerto 8000)..." -ForegroundColor Green

# Verificar que la API esté corriendo en puerto 8000 (sin Nginx)
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API respondiendo correctamente en puerto 8000" -ForegroundColor Green
    } else {
        throw "Status code: $($response.StatusCode)"
    }
} catch {
    Write-Host "❌ La API no está respondiendo en localhost:8000" -ForegroundColor Red
    Write-Host "💡 Asegúrate de que docker-compose esté corriendo con la configuración simple" -ForegroundColor Yellow
    Write-Host "💡 Verifica: docker ps | findstr cinemax_api" -ForegroundColor Yellow
    Write-Host "💡 O inicia tu API manualmente: python main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "🌐 Iniciando túnel rápido..." -ForegroundColor Blue
Write-Host "📝 Presiona Ctrl+C para detener el túnel" -ForegroundColor Yellow

# Iniciar túnel rápido (no requiere dominio)
cloudflared tunnel --url http://localhost:8000 