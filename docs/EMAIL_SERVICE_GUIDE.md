# Sistema de Correo Electrónico con Redis

## Descripción

El sistema de correo electrónico utiliza Redis Streams para enviar notificaciones de manera asíncrona y confiable. Esto permite que las transacciones se completen rápidamente mientras los correos se procesan en segundo plano.

## Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  Redis Streams  │───▶│  Email Service  │
│                 │    │                 │    │                 │
│ - Transacciones │    │ - email:notif   │    │ - SMTP/API      │
│ - Confirmación  │    │ - email:queue   │    │ - Templates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Componentes

### 1. EmailService (`services/email_service.py`)

Servicio principal que maneja el envío de correos usando Redis Streams.

#### Métodos Principales:

- `enviar_correo_confirmacion_compra()`: Envía confirmación de compra exitosa
- `enviar_correo_cancelacion()`: Envía notificación de cancelación
- `enviar_correo_recordatorio()`: Envía recordatorio de función
- `procesar_cola_correos()`: Procesa correos pendientes
- `obtener_estadisticas_correos()`: Obtiene estadísticas

### 2. Integración con Transacciones

El servicio se integra automáticamente en el caso de uso de compra de entradas:

```python
# En use_cases/comprar_entrada_use_case.py
if resultado_pago["exitoso"]:
    # Enviar correo de confirmación
    await email_service.enviar_correo_confirmacion_compra(
        email=usuario.email,
        transaccion_data=transaccion_data
    )
```

## Tipos de Correos

### 1. Confirmación de Compra

**Trigger**: Transacción confirmada exitosamente
**Contenido**:
- Número de factura
- Asientos comprados
- Total pagado
- Método de pago
- Código QR para entrada
- Fecha de vencimiento

**Template**: `confirmacion_compra`

### 2. Cancelación de Transacción

**Trigger**: Usuario cancela transacción
**Contenido**:
- Número de factura
- Motivo de cancelación
- Información de reembolso
- Fecha de cancelación

**Template**: `cancelacion_compra`

### 3. Recordatorio de Función

**Trigger**: Programado (antes de la función)
**Contenido**:
- Nombre de la película
- Fecha y hora de la función
- Sala
- Asientos reservados
- Código QR

**Template**: `recordatorio_funcion`

## Endpoints de Administración

### Procesar Cola de Correos

```http
POST /api/v1/transacciones/procesar-correos
Authorization: Bearer <token>
Content-Type: application/json

{
  "batch_size": 10
}
```

**Respuesta**:
```json
{
  "mensaje": "Se procesaron 5 correos",
  "correos_procesados": 5,
  "batch_size": 10,
  "timestamp": "2024-12-01T12:00:00"
}
```

### Estadísticas de Correos

```http
GET /api/v1/transacciones/estadisticas/correos
Authorization: Bearer <token>
```

**Respuesta**:
```json
{
  "total_correos_enviados": 150,
  "correos_prioridad_alta": 45,
  "fecha_ultima_actualizacion": "2024-12-01T12:00:00"
}
```

## Estructura de Redis

### Streams

- `email:notifications`: Stream principal para correos
- `email:queue`: Cola de prioridad para procesamiento

### Mensaje de Correo

```json
{
  "to": "usuario@ejemplo.com",
  "subject": "Confirmación de Compra - CIN-20241201120000-ABC12345",
  "template": "confirmacion_compra",
  "data": {
    "transaccion_id": "trans_123456789",
    "numero_factura": "CIN-20241201120000-ABC12345",
    "fecha_compra": "2024-12-01T12:00:00",
    "asientos": ["A1", "A2", "B5"],
    "total": 45000,
    "metodo_pago": "tarjeta_credito",
    "estado": "confirmado",
    "fecha_vencimiento": "2024-12-01T12:30:00",
    "codigo_qr": "TRANS123"
  },
  "priority": "high",
  "timestamp": "2024-12-01T12:00:00"
}
```

## Configuración

### Variables de Entorno en Docker Compose

El sistema está configurado para usar las variables de entorno definidas en `docker-compose.yml`:

```yaml
environment:
  # Email Configuration
  - SMTP_HOST=smtp.gmail.com
  - SMTP_PORT=587
  - SMTP_USER=cinemax@gmail.com
  - SMTP_PASSWORD=tu-app-password-gmail
  - SMTP_USE_TLS=true
  - SMTP_VERIFY_SSL=true
  - SMTP_MAX_RETRIES=3
  - SMTP_TIMEOUT=30
  - EMAIL_FROM_NAME=Cinemax
  - EMAIL_FROM_ADDRESS=noreply@cinemax.com
  - EMAIL_REPLY_TO=support@cinemax.com
  - ENABLE_EMAIL_NOTIFICATIONS=true
  - EMAIL_BATCH_SIZE=10
  - EMAIL_RETRY_DELAY=5
```

### Variables de Entorno Locales

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password-gmail
SMTP_USE_TLS=true
SMTP_VERIFY_SSL=true
SMTP_MAX_RETRIES=3
SMTP_TIMEOUT=30

# Email Sender Configuration
EMAIL_FROM_NAME=Cinemax
EMAIL_FROM_ADDRESS=noreply@cinemax.com
EMAIL_REPLY_TO=support@cinemax.com

# Email Features
ENABLE_EMAIL_NOTIFICATIONS=true
EMAIL_BATCH_SIZE=10
EMAIL_RETRY_DELAY=5
```

### Configuración de Prioridades

- `high`: Confirmaciones de compra, recordatorios
- `medium`: Cancelaciones, notificaciones generales
- `low`: Newsletters, promociones

## Procesamiento Asíncrono

### Flujo de Procesamiento

1. **Envío**: La aplicación envía correo a Redis Stream
2. **Cola**: El mensaje se agrega a la cola de prioridad
3. **Procesamiento**: Worker procesa correos en lotes
4. **Confirmación**: Se marca como procesado con `XACK`
5. **Estadísticas**: Se actualizan métricas de envío

### Worker de Correos

```python
async def email_worker():
    while True:
        try:
            # Procesar lote de correos
            procesados = await email_service.procesar_cola_correos(batch_size=10)
            
            if procesados > 0:
                print(f"Procesados {procesados} correos")
            
            # Esperar antes del siguiente lote
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Error en worker de correos: {e}")
            await asyncio.sleep(10)
```

## Monitoreo y Métricas

### Métricas Disponibles

- Total de correos enviados
- Correos por prioridad
- Tasa de éxito de envío
- Tiempo promedio de procesamiento
- Correos en cola

### Logs

```
✅ Correo de confirmación enviado a Redis para usuario@ejemplo.com
   ID Mensaje: 1701432000123-0
   Factura: CIN-20241201120000-ABC12345

📧 Correo enviado exitosamente a usuario@ejemplo.com
   Asunto: Confirmación de Compra - CIN-20241201120000-ABC12345
   Template: confirmacion_compra
   Factura: CIN-20241201120000-ABC12345
   Asientos: ['A1', 'A2', 'B5']
   Total: $45,000
```

## Pruebas

### Script de Prueba

```bash
python test_email_service.py
```

### Pruebas Manuales

1. **Comprar entrada**: Realizar una compra y verificar que se envía correo
2. **Cancelar transacción**: Cancelar y verificar correo de cancelación
3. **Procesar cola**: Usar endpoint para procesar correos pendientes
4. **Ver estadísticas**: Consultar métricas de correos

## Ventajas del Sistema

### 1. Asíncrono
- Las transacciones no se bloquean esperando envío de correos
- Mejor experiencia de usuario
- Mayor throughput

### 2. Confiable
- Redis Streams garantiza persistencia
- Reintentos automáticos
- Confirmación de procesamiento

### 3. Escalable
- Procesamiento en lotes
- Múltiples workers
- Colas de prioridad

### 4. Monitoreable
- Métricas en tiempo real
- Logs detallados
- Estadísticas de rendimiento

## Configuración de Gmail para Envío de Correos

### 1. Habilitar Autenticación de 2 Factores
1. Ve a tu cuenta de Google
2. Activa la verificación en 2 pasos
3. Ve a "Contraseñas de aplicación"

### 2. Generar Contraseña de Aplicación
1. Selecciona "Correo" como aplicación
2. Copia la contraseña generada (16 caracteres)
3. Usa esta contraseña en `SMTP_PASSWORD`

### 3. Configurar Variables de Entorno
```bash
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Contraseña de aplicación
```

## Implementación en Producción

### 1. Configurar SMTP Real

```python
# En email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def enviar_correo_real(self, email_data):
    # Configurar SMTP
    smtp_server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    smtp_server.starttls()
    smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    
    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USER
    msg['To'] = email_data['to']
    msg['Subject'] = email_data['subject']
    
    # Agregar contenido
    msg.attach(MIMEText(self.render_template(email_data), 'html'))
    
    # Enviar
    smtp_server.send_message(msg)
    smtp_server.quit()
```

### 2. Templates HTML

```html
<!-- templates/confirmacion_compra.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Confirmación de Compra</title>
</head>
<body>
    <h1>¡Compra Confirmada!</h1>
    <p>Factura: {{ numero_factura }}</p>
    <p>Asientos: {{ asientos|join(', ') }}</p>
    <p>Total: ${{ total|format_number }}</p>
    <p>Código QR: {{ codigo_qr }}</p>
</body>
</html>
```

### 3. Worker en Background

```python
# workers/email_worker.py
import asyncio
from services.email_service import email_service

async def main():
    await email_service.connect()
    
    while True:
        try:
            await email_service.procesar_cola_correos(batch_size=20)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Problemas Comunes

1. **Redis no disponible**
   - Verificar conexión a Redis
   - Revisar configuración de host/port

2. **Correos no se procesan**
   - Verificar worker de correos
   - Revisar logs de procesamiento

3. **Errores de SMTP**
   - Verificar credenciales
   - Revisar configuración de servidor

### Comandos de Diagnóstico

```bash
# Verificar conexión a Redis
redis-cli ping

# Ver correos en cola
redis-cli XRANGE email:notifications - +

# Ver estadísticas
redis-cli ZCARD email:queue
```

## Seguridad

### Consideraciones

1. **Encriptación**: Usar TLS para conexiones SMTP
2. **Autenticación**: Validar tokens JWT para endpoints admin
3. **Rate Limiting**: Limitar envío de correos por usuario
4. **Logs**: No registrar información sensible en logs

### Configuración Segura

```python
# Configuración segura de SMTP
SMTP_USE_TLS = True
SMTP_VERIFY_SSL = True
SMTP_MAX_RETRIES = 3
SMTP_TIMEOUT = 30
```

## Conclusión

El sistema de correo electrónico con Redis proporciona una solución robusta, escalable y confiable para el envío de notificaciones en el sistema de cine. La arquitectura asíncrona garantiza una excelente experiencia de usuario mientras mantiene la confiabilidad del sistema. 