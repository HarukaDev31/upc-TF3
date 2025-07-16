# Script mejorado para configurar port forwarding en Windows para WSL2
# Uso: .\scripts\setup-port-forwarding-fixed.ps1

param(
    [string]$WslIp = "172.25.192.1"
)

# Colores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Función para logging
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

Write-Host "🌐 Configurando Port Forwarding para WSL2..." -ForegroundColor $Blue

# Verificar si estamos ejecutando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Este script debe ejecutarse como administrador"
    Write-Host "Por favor, ejecuta PowerShell como administrador y vuelve a intentar" -ForegroundColor $Yellow
    exit 1
}

# Obtener IP de WSL2 si no se proporciona
if ([string]::IsNullOrEmpty($WslIp)) {
    Write-Log "Obteniendo IP de WSL2..." $Blue
    
    # Intentar diferentes métodos para obtener la IP
    try {
        # Método 1: Usar ip route
        $WslIp = (wsl ip route show | Select-String "default" | ForEach-Object { ($_ -split '\s+')[2] }).Trim()
        if ([string]::IsNullOrEmpty($WslIp)) {
            throw "No se pudo obtener IP con ip route"
        }
    } catch {
        try {
            # Método 2: Usar ip addr
            $WslIp = (wsl ip addr show eth0 | Select-String "inet " | ForEach-Object { ($_ -split '\s+')[1] -split '/' | Select-Object -First 1 }).Trim()
            if ([string]::IsNullOrEmpty($WslIp)) {
                throw "No se pudo obtener IP con ip addr"
            }
        } catch {
            try {
                # Método 3: Usar hostname -i (si está disponible)
                $WslIp = (wsl hostname -i 2>$null).Trim()
                if ([string]::IsNullOrEmpty($WslIp)) {
                    throw "No se pudo obtener IP con hostname"
                }
            } catch {
                Write-Error "No se pudo obtener la IP de WSL2 automáticamente"
                Write-Host "Por favor, proporciona la IP manualmente:" -ForegroundColor $Yellow
                Write-Host "  1. Ejecuta 'wsl ip route show' en WSL2" -ForegroundColor White
                Write-Host "  2. Busca la línea que empiece con 'default via'" -ForegroundColor White
                Write-Host "  3. La tercera columna es tu IP" -ForegroundColor White
                Write-Host "  4. Ejecuta: .\scripts\setup-port-forwarding-fixed.ps1 -WslIp 'TU_IP_AQUI'" -ForegroundColor White
                exit 1
            }
        }
    }
}

Write-Success "IP de WSL2 detectada: $WslIp"

# Configurar port forwarding para diferentes puertos
$Ports = @(8080, 8443, 3000, 8081, 8082, 9090)

foreach ($port in $Ports) {
    Write-Log "Configurando port forwarding para puerto $port..." $Blue
    
    # Eliminar regla existente si existe
    try {
        netsh interface portproxy delete v4tov4 listenport=$port 2>$null
        Write-Log "Regla existente eliminada para puerto $port" $Yellow
    } catch {
        # Ignorar si no existe la regla
    }
    
    # Agregar nueva regla
    try {
        netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$WslIp
        Write-Success "Port forwarding configurado para puerto $port"
    } catch {
        Write-Error "Error al configurar port forwarding para puerto $port"
    }
}

# Configurar firewall de Windows
Write-Log "Configurando firewall de Windows..." $Blue

foreach ($port in $Ports) {
    try {
        # Permitir tráfico entrante
        New-NetFirewallRule -DisplayName "WSL2 Port $port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -ErrorAction SilentlyContinue
        Write-Success "Regla de firewall agregada para puerto $port"
    } catch {
        Write-Warning "Error al configurar firewall para puerto $port"
    }
}

# Mostrar reglas configuradas
Write-Log "Mostrando reglas de port forwarding configuradas:" $Blue
netsh interface portproxy show all

# Mostrar información de conectividad
Write-Host ""
Write-Host "🎉 ¡Port forwarding configurado exitosamente!" -ForegroundColor $Green
Write-Host ""
Write-Host "📋 Información de conectividad:" -ForegroundColor $Blue
Write-Host "   🌐 IP WSL2: $WslIp" -ForegroundColor White
Write-Host "   🌐 API Principal: http://localhost:8080" -ForegroundColor White
Write-Host "   📚 Documentación: http://localhost:8080/docs" -ForegroundColor White
Write-Host "   🔌 WebSocket: ws://localhost:8080/ws/" -ForegroundColor White
Write-Host "   📊 Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "   🗄️  MongoDB Express: http://localhost:8081" -ForegroundColor White
Write-Host "   🔴 Redis Commander: http://localhost:8082" -ForegroundColor White
Write-Host "   📈 Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "🌍 Para acceso desde internet:" -ForegroundColor $Blue
Write-Host "   📝 Configura tu router para port forwarding" -ForegroundColor White
Write-Host "   📝 Usa ngrok para exposición temporal" -ForegroundColor White
Write-Host "   📝 Configura un dominio y DNS" -ForegroundColor White
Write-Host ""
Write-Host "📝 Comandos útiles:" -ForegroundColor $Blue
Write-Host "   Ver reglas: netsh interface portproxy show all" -ForegroundColor White
Write-Host "   Eliminar regla: netsh interface portproxy delete v4tov4 listenport=80" -ForegroundColor White
Write-Host "   Verificar conectividad: curl http://localhost/health" -ForegroundColor White
Write-Host ""

Write-Success "¡Port forwarding configurado! Tu API está lista para ser accedida desde internet." 