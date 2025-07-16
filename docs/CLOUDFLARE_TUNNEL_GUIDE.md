# 🌐 Guía de Cloudflare Tunnel - Cinemax API

Guía completa para exponer tu API de Cinemax a internet usando Cloudflare Tunnel de forma segura.

## 🎯 ¿Por qué Cloudflare Tunnel?

### ✅ Ventajas:
- **HTTPS automático** - Sin configuración adicional
- **Seguridad mejorada** - No expone puertos al internet
- **URLs fijas** - No cambian como ngrok
- **Gratuito** - Para uso personal y desarrollo
- **Fácil configuración** - Scripts automatizados

### 🔒 Seguridad:
- **Sin puertos abiertos** - El túnel es saliente
- **Autenticación automática** - Con tu cuenta de Cloudflare
- **Rate limiting** - Protección contra abuso
- **DDoS protection** - Incluido automáticamente

## 🚀 Configuración Rápida

### Paso 1: Configurar Cloudflare Tunnel
```bash
# En WSL2
cd ~/cinemax-api

# Ejecutar script de configuración
./scripts/setup-cloudflare-tunnel.sh
```

### Paso 2: Configurar DNS
```bash
# En WSL2
./setup-dns.sh
```

### Paso 3: Iniciar el túnel
```bash
# En WSL2
./start-tunnel.sh
```

## 🔧 Configuración Manual

### Paso 1: Instalar cloudflared
```bash
# Descargar e instalar
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
rm cloudflared-linux-amd64.deb
```

### Paso 2: Autenticar con Cloudflare
```bash
# Esto abrirá tu navegador
cloudflared tunnel login
```

### Paso 3: Crear túnel
```bash
# Crear túnel
cloudflared tunnel create cinemax-api

# Listar túnel
cloudflared tunnel list
```

### Paso 4: Configurar túnel
```bash
# Crear directorio de configuración
mkdir -p ~/.cloudflared

# Obtener ID del túnel
TUNNEL_ID=$(cloudflared tunnel list | grep "cinemax-api" | awk '{print $1}')

# Crear configuración
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  # API Principal
  - hostname: api.cinemax.local
    service: http://localhost:8080
  # Documentación
  - hostname: docs.cinemax.local
    service: http://localhost:8080/docs
  # Grafana
  - hostname: grafana.cinemax.local
    service: http://localhost:3000
  # MongoDB Express
  - hostname: mongo.cinemax.local
    service: http://localhost:8081
  # Redis Commander
  - hostname: redis.cinemax.local
    service: http://localhost:8082
  # Prometheus
  - hostname: prometheus.cinemax.local
    service: http://localhost:9090
  # Catch-all rule
  - service: http_status:404
EOF
```

### Paso 5: Configurar DNS
```bash
# Configurar registros DNS
cloudflared tunnel route dns cinemax-api api.cinemax.local
cloudflared tunnel route dns cinemax-api docs.cinemax.local
cloudflared tunnel route dns cinemax-api grafana.cinemax.local
cloudflared tunnel route dns cinemax-api mongo.cinemax.local
cloudflared tunnel route dns cinemax-api redis.cinemax.local
cloudflared tunnel route dns cinemax-api prometheus.cinemax.local
```

### Paso 6: Iniciar túnel
```bash
# Iniciar túnel
cloudflared tunnel run cinemax-api
```

## 🌐 URLs Disponibles

Una vez configurado, tendrás acceso a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API Principal** | https://api.cinemax.local | API REST completa |
| **Documentación** | https://docs.cinemax.local | Swagger UI |
| **Grafana** | https://grafana.cinemax.local | Dashboard (admin/admin123) |
| **MongoDB Express** | https://mongo.cinemax.local | Admin DB (admin/admin123) |
| **Redis Commander** | https://redis.cinemax.local | Admin Redis (admin/admin123) |
| **Prometheus** | https://prometheus.cinemax.local | Métricas |

## 🔄 Gestión del Túnel

### Ver información del túnel
```bash
# Listar túnel
cloudflared tunnel list

# Ver información detallada
cloudflared tunnel info cinemax-api

# Ver logs
cloudflared tunnel info cinemax-api --logfile ~/tunnel.log
```

### Reiniciar túnel
```bash
# Detener túnel (Ctrl+C)
# Luego iniciar de nuevo
cloudflared tunnel run cinemax-api
```

### Eliminar túnel
```bash
# Eliminar túnel
cloudflared tunnel delete cinemax-api

# Limpiar DNS
cloudflared tunnel route dns cinemax-api --delete
```

## 🎯 Configuración para Producción

### Usar dominio real
```bash
# En lugar de .local, usa tu dominio
cloudflared tunnel route dns cinemax-api api.tudominio.com
cloudflared tunnel route dns cinemax-api docs.tudominio.com
```

### Configuración avanzada
```yaml
# ~/.cloudflared/config.yml
tunnel: TU_TUNNEL_ID
credentials-file: ~/.cloudflared/TU_TUNNEL_ID.json

ingress:
  # API con autenticación
  - hostname: api.tudominio.com
    service: http://localhost:8080
    originRequest:
      noTLSVerify: true
  # Documentación
  - hostname: docs.tudominio.com
    service: http://localhost:8080/docs
  # Catch-all
  - service: http_status:404
```

## 🚨 Troubleshooting

### Problema: Túnel no inicia
```bash
# Verificar autenticación
cloudflared tunnel list

# Reautenticar si es necesario
cloudflared tunnel login
```

### Problema: URLs no funcionan
```bash
# Verificar que la API esté corriendo
curl http://localhost:8080/health

# Verificar configuración del túnel
cloudflared tunnel info cinemax-api
```

### Problema: DNS no resuelve
```bash
# Verificar registros DNS
cloudflared tunnel route dns cinemax-api --list

# Recrear registros DNS
./setup-dns.sh
```

### Problema: Certificados SSL
```bash
# Los certificados son automáticos con Cloudflare
# Si hay problemas, verificar configuración
cloudflared tunnel info cinemax-api
```

## 📊 Monitoreo

### Ver estadísticas del túnel
```bash
# Ver información del túnel
cloudflared tunnel info cinemax-api

# Ver logs en tiempo real
cloudflared tunnel run cinemax-api --loglevel debug
```

### Health checks
```bash
# Verificar que todo funcione
curl https://api.cinemax.local/health
curl https://docs.cinemax.local
```

## 🔒 Seguridad Avanzada

### Configurar acceso restringido
```yaml
# ~/.cloudflared/config.yml
ingress:
  # Solo para IPs específicas
  - hostname: admin.cinemax.local
    service: http://localhost:3000
    originRequest:
      ipRules:
        - prefix: "192.168.1.0/24"
          ports: [80, 443]
          allow: true
```

### Configurar headers personalizados
```yaml
ingress:
  - hostname: api.cinemax.local
    service: http://localhost:8080
    originRequest:
      headers:
        - name: X-Custom-Header
          value: "Cinemax-API"
```

## 🎉 ¡Listo!

Una vez configurado, tu API estará disponible de forma segura en internet con:

- ✅ **HTTPS automático**
- ✅ **URLs fijas**
- ✅ **Sin puertos abiertos**
- ✅ **Protección DDoS**
- ✅ **Rate limiting**

¡Tu sistema de cine está listo para el mundo! 🎬🌐 