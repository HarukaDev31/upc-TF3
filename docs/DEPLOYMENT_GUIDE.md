# 🚀 Guía de Despliegue Automático - Cinemax API

Esta guía te ayudará a desplegar automáticamente la API de Cinemax en tu servidor con Nginx como proxy inverso.

## 📋 Prerrequisitos

### En tu servidor necesitas:
- **Docker** (versión 20.10+)
- **Docker Compose** (versión 2.0+)
- **Git** (versión 2.30+)
- **Puertos disponibles**: 80, 443, 3000, 8081, 8082, 9090

### Verificar instalaciones:
```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker-compose --version

# Verificar Git
git --version
```

## 🎯 Despliegue Automático

### Opción 1: Linux/Mac (Bash)
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/cinemax-api.git
cd cinemax-api

# Ejecutar script de despliegue
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Opción 2: Windows (PowerShell)
```powershell
# Clonar el repositorio
git clone https://github.com/tu-usuario/cinemax-api.git
cd cinemax-api

# Ejecutar script de despliegue
.\scripts\deploy.ps1
```

### Opción 3: Despliegue Manual
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/cinemax-api.git
cd cinemax-api

# 2. Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# 3. Levantar servicios
docker-compose up -d --build

# 4. Verificar estado
docker-compose ps
```

## 🌐 Configuración de Nginx

El servicio de Nginx actúa como proxy inverso y proporciona:

### ✅ Características implementadas:
- **Proxy inverso** para la API de FastAPI
- **Soporte WebSocket** para tiempo real
- **Compresión Gzip** para mejor rendimiento
- **Rate limiting** para protección contra abuso
- **Headers de seguridad** (CORS, XSS, etc.)
- **Logging** detallado de acceso y errores
- **Health checks** automáticos

### 📁 Estructura de archivos:
```
nginx/
└── nginx.conf          # Configuración principal de Nginx
```

### 🔧 Configuración de puertos:
- **80**: HTTP (Nginx)
- **443**: HTTPS (preparado para SSL)
- **8000**: API (interno, no expuesto)
- **3000**: Grafana
- **8081**: MongoDB Express
- **8082**: Redis Commander
- **9090**: Prometheus

## 📊 Servicios incluidos

| Servicio | Puerto | URL | Usuario/Contraseña |
|----------|--------|-----|-------------------|
| **API Principal** | 80 | http://localhost | - |
| **Documentación** | 80 | http://localhost/docs | - |
| **WebSocket** | 80 | ws://localhost/ws/ | - |
| **Grafana** | 3000 | http://localhost:3000 | admin/admin123 |
| **MongoDB Express** | 8081 | http://localhost:8081 | admin/admin123 |
| **Redis Commander** | 8082 | http://localhost:8082 | admin/admin123 |
| **Prometheus** | 9090 | http://localhost:9090 | - |

## 🔒 Configuración de Seguridad

### Variables de entorno críticas:
```bash
# Cambiar en producción
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion
MONGODB_ROOT_PASSWORD=password123
REDIS_PASSWORD=redis123
```

### Configuraciones de seguridad en Nginx:
- Rate limiting: 10 req/s para API, 30 req/s para WebSocket
- Headers de seguridad automáticos
- Protección contra XSS y clickjacking
- Timeouts configurados apropiadamente

## 📈 Monitoreo y Logs

### Ver logs en tiempo real:
```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f api
docker-compose logs -f nginx
docker-compose logs -f mongodb
```

### Logs de Nginx:
```bash
# Acceso
docker exec cinemax_nginx cat /var/log/nginx/access.log

# Errores
docker exec cinemax_nginx cat /var/log/nginx/error.log
```

### Métricas disponibles:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)

## 🔄 Actualización y Mantenimiento

### Actualizar a la última versión:
```bash
# Linux/Mac
./scripts/deploy.sh

# Windows
.\scripts\deploy.ps1
```

### Comandos útiles:
```bash
# Reiniciar servicios
docker-compose restart

# Reiniciar servicio específico
docker-compose restart api

# Ver estado de servicios
docker-compose ps

# Detener todos los servicios
docker-compose down

# Detener y limpiar volúmenes
docker-compose down -v
```

## 🚨 Troubleshooting

### Problema: API no responde
```bash
# Verificar logs de la API
docker-compose logs api

# Verificar health check
curl http://localhost/health

# Verificar contenedores
docker-compose ps
```

### Problema: Nginx no funciona
```bash
# Verificar configuración de Nginx
docker exec cinemax_nginx nginx -t

# Ver logs de Nginx
docker-compose logs nginx

# Reiniciar Nginx
docker-compose restart nginx
```

### Problema: Base de datos no conecta
```bash
# Verificar MongoDB
docker-compose logs mongodb

# Verificar Redis
docker-compose logs redis

# Conectar a MongoDB
docker exec -it cinemax_mongodb mongosh -u admin -p password123
```

## 🌍 Configuración para Internet

### Para exponer a internet:

1. **Configurar DNS**:
   ```
   A    tu-dominio.com    -> IP_DEL_SERVIDOR
   ```

2. **Configurar firewall**:
   ```bash
   # Abrir puertos necesarios
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw allow 22
   ```

3. **Configurar SSL/HTTPS** (recomendado):
   ```bash
   # Instalar Certbot
   sudo apt install certbot python3-certbot-nginx

   # Obtener certificado SSL
   sudo certbot --nginx -d tu-dominio.com
   ```

4. **Actualizar configuración de Nginx**:
   - El archivo `nginx.conf` ya está preparado para HTTPS
   - Solo necesitas descomentar las secciones SSL

### Variables de entorno para producción:
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=clave-super-secreta-de-produccion
MONGODB_ROOT_PASSWORD=password-super-seguro
REDIS_PASSWORD=redis-password-seguro
```

## 📞 Soporte

Si tienes problemas con el despliegue:

1. **Verificar logs**: `docker-compose logs -f`
2. **Verificar estado**: `docker-compose ps`
3. **Reiniciar servicios**: `docker-compose restart`
4. **Reconstruir**: `docker-compose up -d --build`

## 🎉 ¡Listo!

Una vez completado el despliegue, tu API estará disponible en:
- **API**: http://tu-servidor.com
- **Documentación**: http://tu-servidor.com/docs
- **WebSocket**: ws://tu-servidor.com/ws/

¡Tu sistema de cine está listo para funcionar en producción! 🎬 