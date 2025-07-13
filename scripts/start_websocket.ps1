# Script PowerShell para levantar solo el servicio WebSocket
Write-Host "🚀 Iniciando servicio WebSocket..." -ForegroundColor Green

# Verificar si Docker está corriendo
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker no está corriendo. Inicia Docker primero." -ForegroundColor Red
    exit 1
}

# Verificar si el puerto 8001 está disponible
$portInUse = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Puerto 8001 está en uso. Deteniendo proceso..." -ForegroundColor Yellow
    Stop-Process -Id $portInUse.OwningProcess -Force
    Start-Sleep -Seconds 2
}

# Levantar solo Redis y API (que incluye WebSocket)
Write-Host "📦 Levantando Redis y API (con WebSocket)..." -ForegroundColor Blue
docker-compose up -d redis api

# Esperar a que Redis esté listo
Write-Host "⏳ Esperando a que Redis esté listo..." -ForegroundColor Yellow
do {
    Write-Host "   Esperando Redis..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
} until (docker-compose exec redis redis-cli ping 2>$null)

Write-Host "✅ Redis está listo" -ForegroundColor Green

# Esperar a que API esté listo
Write-Host "⏳ Esperando a que API esté listo..." -ForegroundColor Yellow
do {
    Write-Host "   Esperando API..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
} until (try { Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Out-Null; $true } catch { $false })

Write-Host "✅ API está listo" -ForegroundColor Green

# Esperar a que WebSocket esté listo
Write-Host "⏳ Esperando a que WebSocket esté listo..." -ForegroundColor Yellow
do {
    Write-Host "   Esperando WebSocket..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
} until (try { Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing | Out-Null; $true } catch { $false })

Write-Host "✅ WebSocket está listo" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Servicio WebSocket iniciado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   WebSocket: ws://localhost:8001/ws/{client_id}" -ForegroundColor White
Write-Host "   Health: http://localhost:8001/health" -ForegroundColor White
Write-Host "   Stats: http://localhost:8001/stats" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Para probar:" -ForegroundColor Cyan
Write-Host "   python test_websocket_service.py" -ForegroundColor White
Write-Host "   python test_websocket_service.py interactive" -ForegroundColor White
Write-Host "   python test_websocket_service.py multi" -ForegroundColor White
Write-Host ""
Write-Host "📝 Logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f api" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Para detener:" -ForegroundColor Cyan
Write-Host "   docker-compose stop api" -ForegroundColor White 