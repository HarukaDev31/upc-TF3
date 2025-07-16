# Script para arreglar la configuración de contraseña de Redis
Write-Host "🔧 Arreglando configuración de contraseña de Redis..." -ForegroundColor Green

Write-Host "📦 Deteniendo servicios..." -ForegroundColor Yellow
docker-compose down

Write-Host "🗑️ Eliminando volumen de Redis..." -ForegroundColor Yellow
docker volume rm upc_redis_data 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Volumen eliminado" -ForegroundColor Green
} else {
    Write-Host "⚠️ Volumen no encontrado o ya eliminado" -ForegroundColor Yellow
}

Write-Host "🚀 Levantando servicios con nueva configuración..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "⏳ Esperando que Redis se inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "🧪 Probando conexión con contraseña..." -ForegroundColor Yellow
try {
    $result = docker exec -it cinemax_redis redis-cli -a redis123 ping 2>&1
    if ($result -like "*PONG*") {
        Write-Host "✅ Redis configurado correctamente con contraseña" -ForegroundColor Green
    } else {
        Write-Host "❌ Error en la configuración" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error probando Redis" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Comandos para probar:" -ForegroundColor Cyan
Write-Host "  docker exec -it cinemax_redis redis-cli -a redis123 ping" -ForegroundColor White
Write-Host "  docker exec -it cinemax_redis redis-benchmark -h 127.0.0.1 -p 6379 -a redis123 -n 10000 -c 50 -q" -ForegroundColor White 