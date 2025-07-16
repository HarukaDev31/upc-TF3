# Script para configurar ngrok para exposición temporal a internet
# Uso: .\scripts\setup-ngrok.ps1

param(
    [string]$NgrokToken = "",
    [int]$Port = 80
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

Write-Host "🌐 Configurando ngrok para exposición temporal..." -ForegroundColor $Blue

# Verificar si ngrok está instalado
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Log "Instalando ngrok..." $Blue
    
    # Descargar ngrok
    $ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    $downloadPath = "$env:TEMP\ngrok.zip"
    $extractPath = "$env:USERPROFILE\ngrok"
    
    try {
        # Crear directorio si no existe
        if (-not (Test-Path $extractPath)) {
            New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
        }
        
        # Descargar ngrok
        Write-Log "Descargando ngrok..." $Blue
        Invoke-WebRequest -Uri $ngrokUrl -OutFile $downloadPath
        
        # Extraer ngrok
        Write-Log "Extrayendo ngrok..." $Blue
        Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
        
        # Mover ngrok.exe a una ubicación en PATH
        $ngrokExe = "$extractPath\ngrok.exe"
        if (Test-Path $ngrokExe) {
            Copy-Item $ngrokExe -Destination "$env:USERPROFILE\AppData\Local\Microsoft\WinGet\Packages" -Force
            $env:PATH += ";$env:USERPROFILE\AppData\Local\Microsoft\WinGet\Packages"
        }
        
        # Limpiar archivo temporal
        Remove-Item $downloadPath -Force -ErrorAction SilentlyContinue
        
        Write-Success "ngrok instalado correctamente"
    } catch {
        Write-Error "Error al instalar ngrok: $($_.Exception.Message)"
        Write-Host "Por favor, descarga ngrok manualmente desde https://ngrok.com/download" -ForegroundColor $Yellow
        exit 1
    }
} else {
    Write-Success "ngrok ya está instalado"
}

# Configurar token de ngrok si se proporciona
if (-not [string]::IsNullOrEmpty($NgrokToken)) {
    Write-Log "Configurando token de ngrok..." $Blue
    try {
        ngrok config add-authtoken $NgrokToken
        Write-Success "Token de ngrok configurado"
    } catch {
        Write-Warning "Error al configurar token de ngrok"
    }
} else {
    Write-Warning "No se proporcionó token de ngrok. Algunas funciones pueden estar limitadas."
    Write-Host "Para obtener un token gratuito, visita: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor $Yellow
}

# Crear script de inicio de ngrok
$ngrokScript = @"
# Script para iniciar ngrok
# Uso: .\start-ngrok.ps1

Write-Host "🌐 Iniciando ngrok para puerto $Port..." -ForegroundColor Green

# Verificar que el puerto esté en uso
try {
    `$response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing -TimeoutSec 5
    if (`$response.StatusCode -eq 200) {
        Write-Host "✅ Puerto $Port está respondiendo" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Puerto $Port no está respondiendo. Asegúrate de que la API esté corriendo." -ForegroundColor Red
    exit 1
}

# Iniciar ngrok
Write-Host "🚀 Iniciando ngrok..." -ForegroundColor Blue
ngrok http $Port --log=stdout

Write-Host "📝 ngrok iniciado. Revisa la consola para ver la URL pública." -ForegroundColor Green
"@

$ngrokScriptPath = ".\scripts\start-ngrok.ps1"
$ngrokScript | Out-File -FilePath $ngrokScriptPath -Encoding UTF8

Write-Success "Script de inicio de ngrok creado en: $ngrokScriptPath"

# Mostrar información
Write-Host ""
Write-Host "🎉 ¡ngrok configurado exitosamente!" -ForegroundColor $Green
Write-Host ""
Write-Host "📋 Información de uso:" -ForegroundColor $Blue
Write-Host "   🚀 Iniciar ngrok: .\scripts\start-ngrok.ps1" -ForegroundColor White
Write-Host "   🌐 URL pública: Se mostrará en la consola de ngrok" -ForegroundColor White
Write-Host "   📊 Dashboard: http://localhost:4040" -ForegroundColor White
Write-Host ""
Write-Host "📝 Pasos para exponer a internet:" -ForegroundColor $Blue
Write-Host "   1. Asegúrate de que la API esté corriendo en WSL2" -ForegroundColor White
Write-Host "   2. Ejecuta: .\scripts\start-ngrok.ps1" -ForegroundColor White
Write-Host "   3. Copia la URL pública que aparece en la consola" -ForegroundColor White
Write-Host "   4. Comparte la URL con quien necesite acceder" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Notas importantes:" -ForegroundColor $Yellow
Write-Host "   - La URL de ngrok cambia cada vez que reinicies ngrok" -ForegroundColor White
Write-Host "   - Para URLs fijas, necesitas una cuenta de ngrok" -ForegroundColor White
Write-Host "   - El tráfico es limitado en la versión gratuita" -ForegroundColor White
Write-Host ""

Write-Success "¡ngrok está listo para usar!" 