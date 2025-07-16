# Script para instalar cloudflared en Windows
Write-Host "🌐 Instalando cloudflared..." -ForegroundColor Green

# Crear directorio temporal
$tempDir = "$env:TEMP\cloudflared"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# URL de descarga para Windows
$downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$outputPath = "$tempDir\cloudflared.exe"

Write-Host "📥 Descargando cloudflared..." -ForegroundColor Blue
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
    Write-Host "✅ Descarga completada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error descargando cloudflared" -ForegroundColor Red
    Write-Host "💡 Descarga manual desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/" -ForegroundColor Yellow
    exit 1
}

# Mover a un directorio en el PATH
$installDir = "$env:USERPROFILE\cloudflared"
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

Copy-Item $outputPath "$installDir\cloudflared.exe"

# Agregar al PATH del usuario
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$installDir", "User")
    Write-Host "✅ Agregado al PATH del usuario" -ForegroundColor Green
}

# Limpiar archivos temporales
Remove-Item $tempDir -Recurse -Force

Write-Host "✅ cloudflared instalado correctamente" -ForegroundColor Green
Write-Host "💡 Reinicia PowerShell para que los cambios en PATH tomen efecto" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Para usar cloudflared:" -ForegroundColor Cyan
Write-Host "  cloudflared tunnel --url http://localhost:8000" -ForegroundColor White 