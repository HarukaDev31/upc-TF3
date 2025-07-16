# Script para detener túneles de Cloudflare
Write-Host "🛑 Deteniendo túneles de Cloudflare..." -ForegroundColor Yellow

# Matar procesos cloudflared
Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "✅ Túneles detenidos" -ForegroundColor Green 