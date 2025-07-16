# Script completo para configurar Cloudflare Tunnel SIN DOMINIO - Cinemax API (Configuración Simple)
# Uso: .\setup-cloudflare-tunnel-simple.ps1

Write-Host "🌐 Configurando Cloudflare Tunnel para Cinemax API (Configuración Simple)..." -ForegroundColor Green

# Verificar si cloudflared está instalado
try {
    $cloudflaredVersion = cloudflared --version 2>$null
    Write-Host "✅ cloudflared ya está instalado: $cloudflaredVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ cloudflared no está instalado" -ForegroundColor Red
    Write-Host "💡 Instala cloudflared desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/" -ForegroundColor Yellow
    exit 1
}

# Crear script para API principal (puerto 8000 - sin Nginx)
Write-Host "📝 Creando script para API principal (puerto 8000)..." -ForegroundColor Blue
$apiScript = @"
# Script para iniciar túnel de API (puerto 8000)
Write-Host "🚀 Iniciando túnel para API Principal (puerto 8000)..." -ForegroundColor Green

# Verificar que la API esté corriendo en puerto 8000 (sin Nginx)
try {
    `$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if (`$response.StatusCode -eq 200) {
        Write-Host "✅ API respondiendo correctamente en puerto 8000" -ForegroundColor Green
    } else {
        throw "Status code: `$(`$response.StatusCode)"
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
"@

$apiScript | Out-File -FilePath "$env:USERPROFILE\start-api-tunnel-simple.ps1" -Encoding UTF8

# Crear script para verificar estado de servicios
Write-Host "📝 Creando script para verificar servicios..." -ForegroundColor Blue
$checkScript = @"
# Script para verificar estado de servicios
Write-Host "🔍 Verificando estado de servicios..." -ForegroundColor Blue

`$services = @(
    @{Name="API Principal"; Port=8000; Path="/health"},
    @{Name="Grafana"; Port=3000; Path=""},
    @{Name="MongoDB Express"; Port=8081; Path=""},
    @{Name="Redis Commander"; Port=8082; Path=""},
    @{Name="Prometheus"; Port=9090; Path=""}
)

foreach (`$service in `$services) {
    try {
        `$url = "http://localhost:`$(`$service.Port)`$(`$service.Path)"
        `$response = Invoke-WebRequest -Uri `$url -UseBasicParsing -TimeoutSec 3
        Write-Host "✅ `$(`$service.Name) (puerto `$(`$service.Port)): `$(`$response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ `$(`$service.Name) (puerto `$(`$service.Port)): No responde" -ForegroundColor Red
    }
}
"@

$checkScript | Out-File -FilePath "$env:USERPROFILE\check-services.ps1" -Encoding UTF8

# Crear script para iniciar túnel simple
Write-Host "📝 Creando script para iniciar túnel simple..." -ForegroundColor Blue
$simpleTunnelScript = @"
# Script para iniciar túnel simple para API
Write-Host "🚀 Iniciando túnel simple para API..." -ForegroundColor Green

# Verificar que la API esté corriendo
try {
    `$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ API respondiendo correctamente" -ForegroundColor Green
} catch {
    Write-Host "❌ La API no está respondiendo en localhost:8000" -ForegroundColor Red
    Write-Host "💡 Asegúrate de que docker-compose esté corriendo" -ForegroundColor Yellow
    Write-Host "💡 Ejecuta: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "🌐 Iniciando túnel de Cloudflare..." -ForegroundColor Blue
Write-Host "📝 Presiona Ctrl+C para detener el túnel" -ForegroundColor Yellow

# Iniciar túnel
cloudflared tunnel --url http://localhost:8000
"@

$simpleTunnelScript | Out-File -FilePath "$env:USERPROFILE\start-simple-tunnel.ps1" -Encoding UTF8

# Crear script para detener túneles
Write-Host "📝 Creando script para detener túneles..." -ForegroundColor Blue
$stopScript = @"
# Script para detener túneles de Cloudflare
Write-Host "🛑 Deteniendo túneles de Cloudflare..." -ForegroundColor Yellow

# Matar procesos cloudflared
Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "✅ Túneles detenidos" -ForegroundColor Green
"@

$stopScript | Out-File -FilePath "$env:USERPROFILE\stop-tunnels.ps1" -Encoding UTF8

Write-Host "✅ Scripts de Cloudflare Tunnel creados correctamente" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Scripts disponibles:" -ForegroundColor Cyan
Write-Host "  - `$env:USERPROFILE\start-api-tunnel-simple.ps1     # Solo API (puerto 8000)" -ForegroundColor White
Write-Host "  - `$env:USERPROFILE\start-simple-tunnel.ps1          # Túnel simple" -ForegroundColor White
Write-Host "  - `$env:USERPROFILE\check-services.ps1               # Verificar servicios" -ForegroundColor White
Write-Host "  - `$env:USERPROFILE\stop-tunnels.ps1                 # Detener túneles" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para iniciar solo la API:" -ForegroundColor Cyan
Write-Host "  . `$env:USERPROFILE\start-api-tunnel-simple.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para iniciar túnel simple:" -ForegroundColor Cyan
Write-Host "  . `$env:USERPROFILE\start-simple-tunnel.ps1" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Asegúrate de que docker-compose esté corriendo con la configuración simple" -ForegroundColor Yellow
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URL que se generará:" -ForegroundColor Cyan
Write-Host "  - API: https://[random].trycloudflare.com" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Para probar la API localmente:" -ForegroundColor Cyan
Write-Host "  curl http://localhost:8000/health" -ForegroundColor White
Write-Host "  curl http://localhost:8000/api/v1/peliculas/list?limite=12&offset=0" -ForegroundColor White 