# 🚀 Guía de Despliegue en WSL2 - Cinemax API

Guía completa para desplegar la API de Cinemax en WSL2 y exponerla a internet usando port forwarding y ngrok.

## 📋 Prerrequisitos

### 1. WSL2 Configurado
- **WSL2** instalado y funcionando
- **Ubuntu** 20.04 LTS o 22.04 LTS en WSL2
- **Docker Desktop** para Windows (opcional, pero recomendado)

### 2. Verificar WSL2
```powershell
# En PowerShell como administrador
wsl --list --verbose
```

## 🎯 Despliegue Automático

### Paso 1: Desplegar en WSL2
```bash
# Conectar a WSL2
wsl

# Navegar al directorio del proyecto
cd ~/cinemax-api

# Ejecutar script de despliegue
./scripts/deploy-wsl2.sh
```

### Paso 2: Configurar Port Forwarding en Windows
```powershell
# En PowerShell como administrador
.\scripts\setup-port-forwarding.ps1
```

### Paso 3: Configurar ngrok (Opcional)
```powershell
# En PowerShell
.\scripts\setup-ngrok.ps1

# O con token personalizado
.\scripts\setup-ngrok.ps1 -NgrokToken "tu-token-aqui"
```

## 🔧 Despliegue Manual

### Paso 1: Instalar dependencias en WSL2
```bash
# Actualizar sistema
sudo apt-get update

# Instalar Docker
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Git
sudo apt-get install -y git
```

### Paso 2: Clonar y configurar el proyecto
```bash
# Crear directorio del proyecto
mkdir -p ~/cinemax-api
cd ~/cinemax-api

# Clonar repositorio
git clone https://github.com/tu-usuario/cinemax-api.git .

# Configurar variables de entorno
cp env.example .env
```

### Paso 3: Levantar servicios
```bash
# Construir y levantar servicios
docker-compose up -d --build

# Verificar estado
docker-compose ps
```

## 🌐 Configuración de Port Forwarding

### Método 1: Script Automático (Recomendado)
```powershell
# Ejecutar como administrador
.\scripts\setup-port-forwarding.ps1
```

### Método 2: Manual
```powershell
# Obtener IP de WSL2
$wslIp = (wsl hostname -I).Trim()

# Configurar port forwarding para puerto 80
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=80 connectaddress=$wslIp

# Configurar firewall
New-NetFirewallRule -DisplayName "WSL2 Port 80" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

### Método 3: Usando netsh directamente
```powershell
# Configurar todos los puertos necesarios
$ports = @(80, 443, 3000, 8081, 8082, 9090)
$wslIp = (wsl hostname -I).Trim()

foreach ($port in $ports) {
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    New-NetFirewallRule -DisplayName "WSL2 Port $port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow
}
```

## 🌍 Exposición a Internet

### Opción 1: ngrok (Recomendado para pruebas)
```powershell
# Configurar ngrok
.\scripts\setup-ngrok.ps1

# Iniciar ngrok
.\scripts\start-ngrok.ps1
```

### Opción 2: Port Forwarding del Router
1. **Obtener IP pública de tu router**
2. **Configurar port forwarding en el router**
3. **Abrir puertos 80, 443, 3000, 8081, 8082, 9090**

### Opción 3: Servicio de Túnel (Cloudflare Tunnel)
```bash
# Instalar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Autenticar
cloudflared tunnel login

# Crear túnel
cloudflared tunnel create cinemax-api

# Configurar túnel
cloudflared tunnel route dns cinemax-api tu-dominio.com
```

## 📊 Servicios Disponibles

| Servicio | Puerto | URL Local | URL Pública |
|----------|--------|-----------|-------------|
| **API Principal** | 80 | http://localhost | http://tu-ip-publica |
| **Documentación** | 80 | http://localhost/docs | http://tu-ip-publica/docs |
| **WebSocket** | 80 | ws://localhost/ws/ | ws://tu-ip-publica/ws/ |
| **Grafana** | 3000 | http://localhost:3000 | http://tu-ip-publica:3000 |
| **MongoDB Express** | 8081 | http://localhost:8081 | http://tu-ip-publica:8081 |
| **Redis Commander** | 8082 | http://localhost:8082 | http://tu-ip-publica:8082 |
| **Prometheus** | 9090 | http://localhost:9090 | http://tu-ip-publica:9090 |

## 🔒 Configuración de Seguridad

### Variables de entorno para desarrollo
```bash
# En WSL2, editar .env
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=clave-de-desarrollo
MONGODB_ROOT_PASSWORD=password123
REDIS_PASSWORD=redis123
```

### Configuraciones de firewall
```powershell
# Verificar reglas de firewall
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*WSL2*"}

# Eliminar reglas específicas
Remove-NetFirewallRule -DisplayName "WSL2 Port 80"
```

## 📈 Monitoreo y Logs

### Ver logs en tiempo real
```bash
# En WSL2
docker-compose logs -f

# Servicio específico
docker-compose logs -f api
docker-compose logs -f nginx
```

### Health checks
```bash
# Verificar API
curl http://localhost/health

# Verificar métricas
curl http://localhost/metrics
```

### Monitoreo de recursos
```bash
# Ver uso de recursos
docker stats

# Ver puertos abiertos
netstat -tulpn
```

## 🚨 Troubleshooting

### Problema: API no responde desde Windows
```powershell
# Verificar port forwarding
netsh interface portproxy show all

# Verificar IP de WSL2
wsl hostname -I

# Verificar conectividad
Test-NetConnection -ComputerName localhost -Port 80
```

### Problema: Docker no inicia en WSL2
```bash
# Verificar servicio Docker
sudo systemctl status docker

# Reiniciar Docker
sudo systemctl restart docker

# Verificar permisos
sudo usermod -aG docker $USER
```

### Problema: ngrok no funciona
```powershell
# Verificar instalación de ngrok
ngrok version

# Verificar token
ngrok config check

# Reinstalar ngrok
.\scripts\setup-ngrok.ps1
```

### Problema: Puertos bloqueados
```powershell
# Verificar firewall de Windows
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*WSL2*"}

# Verificar port forwarding
netsh interface portproxy show all

# Eliminar y recrear reglas
netsh interface portproxy delete v4tov4 listenport=80
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=80 connectaddress=$wslIp
```

## 🔄 Actualización y Mantenimiento

### Actualizar a la última versión
```bash
# En WSL2
cd ~/cinemax-api
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Comandos útiles de mantenimiento
```bash
# Ver uso de recursos
docker stats

# Limpiar imágenes no utilizadas
docker system prune -a

# Verificar espacio en disco
df -h

# Ver logs de sistema
sudo journalctl -u docker
```

## 📞 Soporte y Monitoreo

### Alertas automáticas
```bash
# Configurar monitoreo básico
# Crear script de health check
cat > health-check.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost/health &> /dev/null; then
    echo "API no responde - $(date)" >> /tmp/api-health.log
    # Aquí puedes agregar notificaciones
fi
EOF

chmod +x health-check.sh
```

### Logs centralizados
```bash
# Configurar rotación de logs
sudo logrotate -f /etc/logrotate.conf

# Configurar logs de Docker
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
```

## 🎉 ¡Listo!

Una vez completado el despliegue, tu API estará disponible en:
- **Local**: http://localhost
- **Pública**: http://tu-ip-publica (con port forwarding)
- **Temporal**: https://tu-url-ngrok.ngrok.io (con ngrok)

### Verificación final
```bash
# Verificar que todo funcione
curl http://localhost/health
curl http://localhost/api/v1/peliculas

# Verificar WebSocket
wscat -c ws://localhost/ws/
```

¡Tu sistema de cine está listo para funcionar en WSL2 y ser expuesto a internet! 🎬🌐 