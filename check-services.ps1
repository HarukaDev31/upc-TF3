# Script para verificar estado de servicios
Write-Host "🔍 Verificando estado de servicios..." -ForegroundColor Blue

$services = @(
    @{Name="API Principal"; Port=8000; Path="/health"},
    @{Name="Grafana"; Port=3000; Path=""},
    @{Name="MongoDB Express"; Port=8081; Path=""},
    @{Name="Redis Commander"; Port=8082; Path=""},
    @{Name="Prometheus"; Port=9090; Path=""}
)

foreach ($service in $services) {
    try {
        $url = "http://localhost:$($service.Port)$($service.Path)"
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        Write-Host "✅ $($service.Name) (puerto $($service.Port)): $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($service.Name) (puerto $($service.Port)): No responde" -ForegroundColor Red
    }
} 