# Script de despliegue automático para Cinemax API (Windows)
# Uso: .\scripts\deploy.ps1

param(
    [string]$ProjectDir = "C:\cinemax-api"
)

# Configurar para salir en caso de error
$ErrorActionPreference = "Stop"

Write-Host "🎬 Iniciando despliegue automático de Cinemax API..." -ForegroundColor Blue

# Función para logging
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Verificar si Docker está instalado
try {
    docker --version | Out-Null
    Write-Success "Docker está instalado"
} catch {
    Write-Error "Docker no está instalado. Por favor instala Docker Desktop primero."
    exit 1
}

# Verificar si Docker Compose está instalado
try {
    docker-compose --version | Out-Null
    Write-Success "Docker Compose está instalado"
} catch {
    Write-Error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
}

# Verificar si git está instalado
try {
    git --version | Out-Null
    Write-Success "Git está instalado"
} catch {
    Write-Error "Git no está instalado. Por favor instala Git primero."
    exit 1
}

Write-Log "Verificando dependencias..." "Blue"
Write-Success "Todas las dependencias están instaladas"

# Crear directorio del proyecto si no existe
if (-not (Test-Path $ProjectDir)) {
    Write-Log "Creando directorio del proyecto..." "Blue"
    New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
}

# Navegar al directorio del proyecto
Set-Location $ProjectDir

# Clonar o actualizar el repositorio
if (Test-Path ".git") {
    Write-Log "Actualizando repositorio existente..." "Blue"
    git pull origin main
} else {
    Write-Log "Clonando repositorio..." "Blue"
    git clone https://github.com/tu-usuario/cinemax-api.git .
}

# Crear archivo .env si no existe
if (-not (Test-Path ".env")) {
    Write-Log "Creando archivo .env..." "Blue"
    Copy-Item "env.example" ".env"
    Write-Warning "Por favor edita el archivo .env con tus configuraciones de producción"
}

# Crear directorio de logs si no existe
if (-not (Test-Path "logs")) {
    Write-Log "Creando directorio de logs..." "Blue"
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

# Crear directorio nginx si no existe
if (-not (Test-Path "nginx")) {
    Write-Log "Creando directorio nginx..." "Blue"
    New-Item -ItemType Directory -Path "nginx" -Force | Out-Null
}

# Detener contenedores existentes si están corriendo
Write-Log "Deteniendo contenedores existentes..." "Blue"
docker-compose down --remove-orphans

# Limpiar imágenes no utilizadas
Write-Log "Limpiando imágenes Docker no utilizadas..." "Blue"
docker system prune -f

# Construir y levantar los servicios
Write-Log "Construyendo y levantando servicios..." "Blue"
docker-compose up -d --build

# Esperar a que los servicios estén listos
Write-Log "Esperando a que los servicios estén listos..." "Blue"
Start-Sleep -Seconds 30

# Verificar el estado de los servicios
Write-Log "Verificando estado de los servicios..." "Blue"
docker-compose ps

# Verificar que la API esté respondiendo
Write-Log "Verificando que la API esté respondiendo..." "Blue"
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "API está respondiendo correctamente"
            break
        }
    } catch {
        Write-Warning "Intento $i`: API aún no está lista, esperando..."
        Start-Sleep -Seconds 10
    }
}

# Mostrar información del despliegue
Write-Host ""
Write-Host "🎉 ¡Despliegue completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Información del despliegue:" -ForegroundColor Cyan
Write-Host "   🌐 API Principal: http://localhost" -ForegroundColor White
Write-Host "   📚 Documentación: http://localhost/docs" -ForegroundColor White
Write-Host "   🔌 WebSocket: ws://localhost/ws/" -ForegroundColor White
Write-Host "   📊 Grafana: http://localhost:3000 (admin/admin123)" -ForegroundColor White
Write-Host "   🗄️  MongoDB Express: http://localhost:8081 (admin/admin123)" -ForegroundColor White
Write-Host "   🔴 Redis Commander: http://localhost:8082 (admin/admin123)" -ForegroundColor White
Write-Host "   📈 Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "📝 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Ver logs de un servicio: docker-compose logs -f api" -ForegroundColor White
Write-Host "   Reiniciar servicios: docker-compose restart" -ForegroundColor White
Write-Host "   Detener servicios: docker-compose down" -ForegroundColor White
Write-Host "   Actualizar y redeployar: .\scripts\deploy.ps1" -ForegroundColor White
Write-Host ""

# Verificar puertos abiertos
Write-Log "Verificando puertos abiertos..." "Blue"
try {
    $ports = netstat -an | Select-String ":80|:443|:3000|:8081|:8082|:9090"
    if ($ports) {
        Write-Host "Puertos abiertos encontrados:" -ForegroundColor Green
        $ports | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    } else {
        Write-Host "No se encontraron puertos abiertos" -ForegroundColor Yellow
    }
} catch {
    Write-Warning "No se pudo verificar puertos abiertos"
}

Write-Success "¡Despliegue completado! Tu API de Cinemax está lista para usar." 