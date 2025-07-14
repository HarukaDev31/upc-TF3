# 🚀 Guía de Despliegue en EC2 - Cinemax API

Guía completa para desplegar la API de Cinemax en una instancia EC2 de Amazon Linux 2.

## 📋 Prerrequisitos

### 1. Instancia EC2 Configurada
- **AMI**: Ubuntu Server 20.04 LTS o 22.04 LTS
- **Tipo**: t3.medium o superior (recomendado)
- **Almacenamiento**: 20GB mínimo
- **Security Group**: Configurado para puertos 22, 80, 443

### 2. Configuración del Security Group
```bash
# Puertos necesarios para abrir en el Security Group:
- SSH (22)     - Para conexión remota
- HTTP (80)    - API principal
- HTTPS (443)  - SSL (opcional)
- Custom (3000) - Grafana
- Custom (8081) - MongoDB Express
- Custom (8082) - Redis Commander
- Custom (9090) - Prometheus
```

## 🎯 Despliegue Automático (Recomendado)

### Paso 1: Conectar a tu instancia EC2
```bash
# Conectar via SSH
ssh -i tu-key.pem ec2-user@tu-ip-publica

# O si usas AWS CLI
aws ec2 connect --instance-id i-1234567890abcdef0
```

### Paso 2: Ejecutar script de despliegue
```bash
# Descargar el script para Ubuntu
curl -O https://raw.githubusercontent.com/tu-usuario/cinemax-api/main/scripts/deploy-ec2-ubuntu.sh

# Dar permisos de ejecución
chmod +x deploy-ec2-ubuntu.sh

# Ejecutar despliegue
./deploy-ec2-ubuntu.sh
```

### Paso 3: Verificar el despliegue
```bash
# Verificar que los servicios estén corriendo
docker-compose ps

# Verificar que la API responda
curl http://localhost/health

# Verificar logs
docker-compose logs -f
```

## 🔧 Despliegue Manual

### Paso 1: Instalar dependencias
```bash
# Actualizar sistema
sudo apt-get update

# Instalar Docker
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Git
sudo apt-get install -y git
```

### Paso 2: Configurar firewall
```bash
# Instalar y configurar UFW
sudo apt-get install -y ufw
sudo ufw --force enable

# Abrir puertos necesarios
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8081/tcp
sudo ufw allow 8082/tcp
sudo ufw allow 9090/tcp
```

### Paso 3: Clonar y configurar el proyecto
```bash
# Crear directorio del proyecto
mkdir -p /home/ubuntu/cinemax-api
cd /home/ubuntu/cinemax-api

# Clonar repositorio
git clone https://github.com/tu-usuario/cinemax-api.git .

# Configurar variables de entorno
cp env.example .env
```

### Paso 4: Levantar servicios
```bash
# Construir y levantar servicios
docker-compose up -d --build

# Verificar estado
docker-compose ps
```

## 🌐 Configuración de Dominio (Opcional)

### Paso 1: Configurar DNS
```bash
# En tu proveedor de DNS, crear registro A:
# A    tu-dominio.com    -> IP_PUBLICA_DE_EC2
```

### Paso 2: Configurar SSL con Certbot
```bash
# Instalar Certbot
sudo yum install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar línea: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoreo y Logs

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f api
docker-compose logs -f nginx
```

### Health checks
```bash
# Verificar API
curl http://tu-ip-publica/health

# Verificar métricas
curl http://tu-ip-publica/metrics
```

### Monitoreo con CloudWatch
```bash
# Instalar CloudWatch agent
sudo yum install -y amazon-cloudwatch-agent

# Configurar métricas personalizadas
# Crear archivo de configuración para Docker metrics
```

## 🔒 Configuración de Seguridad

### Variables de entorno críticas para producción
```bash
# Editar .env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=clave-super-secreta-de-produccion
MONGODB_ROOT_PASSWORD=password-super-seguro
REDIS_PASSWORD=redis-password-seguro
```

### Configuraciones adicionales de seguridad
```bash
# Configurar límites de memoria para Docker
sudo systemctl edit docker
# Agregar:
# [Service]
# MemoryLimit=2G

# Configurar backup automático
# Crear script de backup para MongoDB
```

## 🚨 Troubleshooting

### Problema: API no responde
```bash
# Verificar contenedores
docker-compose ps

# Verificar logs
docker-compose logs api

# Verificar puertos
netstat -tulpn | grep 80

# Reiniciar servicios
docker-compose restart
```

### Problema: Docker no inicia
```bash
# Verificar servicio Docker
sudo systemctl status docker

# Reiniciar Docker
sudo systemctl restart docker

# Verificar permisos
sudo usermod -a -G docker ec2-user
```

### Problema: Firewall bloquea conexiones
```bash
# Verificar reglas de firewall
sudo ufw status

# Verificar Security Group en AWS Console
# Asegurar que los puertos estén abiertos
```

### Problema: Memoria insuficiente
```bash
# Verificar uso de memoria
free -h

# Limpiar Docker
docker system prune -a

# Configurar swap si es necesario
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 Optimización para Producción

### Configuración de recursos
```bash
# Ajustar límites de memoria en docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Configuración de logs
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

### Configuración de backup
```bash
# Crear script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec cinemax_mongodb mongodump --out /backup/$DATE
docker cp cinemax_mongodb:/backup/$DATE ./backup/
tar -czf backup_$DATE.tar.gz backup/$DATE
aws s3 cp backup_$DATE.tar.gz s3://tu-bucket/backups/
EOF

chmod +x backup.sh
```

## 🔄 Actualización y Mantenimiento

### Actualizar a la última versión
```bash
# Conectar a EC2
ssh -i tu-key.pem ubuntu@tu-ip-publica

# Navegar al proyecto
cd /home/ubuntu/cinemax-api

# Actualizar código
git pull origin main

# Reconstruir y reiniciar
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

# Verificar logs de sistema
sudo journalctl -u docker
```

## 📞 Soporte y Monitoreo

### Alertas automáticas
```bash
# Configurar CloudWatch alarms para:
# - CPU > 80%
# - Memoria > 80%
# - Disco > 85%
# - API no responde
```

### Logs centralizados
```bash
# Configurar CloudWatch Logs
# Enviar logs de Docker a CloudWatch
```

## 🎉 ¡Listo!

Una vez completado el despliegue, tu API estará disponible en:
- **API**: http://tu-ip-publica-ec2
- **Documentación**: http://tu-ip-publica-ec2/docs
- **WebSocket**: ws://tu-ip-publica-ec2/ws/

### Verificación final
```bash
# Verificar que todo funcione
curl http://tu-ip-publica-ec2/health
curl http://tu-ip-publica-ec2/api/v1/peliculas

# Verificar WebSocket
wscat -c ws://tu-ip-publica-ec2/ws/
```

¡Tu sistema de cine está listo para funcionar en la nube de AWS! 🎬☁️ 