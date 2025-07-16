# 🔧 Guía de Solución para Error CORS 307

## 📋 Problema Identificado

Tu frontend en **https://upcfronted.netlify.app** está intentando conectarse a tu API backend en **https://moms-geographic-serial-forget.trycloudflare.com** y recibe un error de CORS 307 (Temporary Redirect).

## 🎯 Soluciones Implementadas

### 1. ✅ Configuración de CORS Mejorada

Se ha creado un archivo de configuración específico para CORS (`config/cors_settings.py`) que incluye:

- **Dominios permitidos**: Tu frontend de Netlify y túneles de Cloudflare
- **Métodos HTTP**: GET, POST, PUT, DELETE, OPTIONS, PATCH
- **Headers permitidos**: Todos los headers necesarios para CORS

### 2. ✅ Endpoint OPTIONS para Preflight

Se agregó un endpoint específico para manejar las peticiones OPTIONS (preflight requests) que son necesarias para CORS.

### 3. ✅ Archivo de Test

Se creó `test_cors_fix.html` para probar la conexión desde el navegador.

## 🚀 Pasos para Aplicar la Solución

### Paso 1: Reiniciar el Servidor

```bash
# Opción 1: Usar el script automático
python restart_server.py

# Opción 2: Manual
# 1. Detener el servidor actual (Ctrl+C)
# 2. Ejecutar: python main.py
```

### Paso 2: Verificar la Configuración

1. Abre tu navegador y ve a: `https://moms-geographic-serial-forget.trycloudflare.com/health`
2. Deberías ver una respuesta JSON con el estado de los servicios

### Paso 3: Probar CORS

1. Abre el archivo `test_cors_fix.html` en tu navegador
2. Haz clic en "Probar Conexión GET"
3. Verifica que no hay errores de CORS

### Paso 4: Actualizar tu Frontend

En tu frontend de Netlify, asegúrate de que las peticiones incluyan los headers correctos:

```javascript
// Ejemplo de petición desde tu frontend
const response = await fetch('https://moms-geographic-serial-forget.trycloudflare.com/api/v1/peliculas?limite=12&offset=0', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});
```

## 🔍 Verificación de la Solución

### Test 1: Health Check
```bash
curl -X GET https://moms-geographic-serial-forget.trycloudflare.com/health
```

### Test 2: Endpoint de Películas
```bash
curl -X GET https://moms-geographic-serial-forget.trycloudflare.com/api/v1/peliculas?limite=12&offset=0
```

### Test 3: OPTIONS (CORS Preflight)
```bash
curl -X OPTIONS https://moms-geographic-serial-forget.trycloudflare.com/api/v1/peliculas \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type, Accept"
```

## 🛠️ Soluciones Alternativas

### Si el problema persiste:

1. **Verificar el túnel de Cloudflare**:
   - Asegúrate de que el túnel esté configurado correctamente
   - Verifica que no haya redirecciones adicionales

2. **Usar un proxy CORS**:
   - Puedes usar servicios como `cors-anywhere` temporalmente
   - O configurar un proxy en tu frontend

3. **Configurar CORS en el túnel**:
   - Si usas Cloudflare Tunnel, puedes configurar CORS directamente en el túnel

## 📝 Logs de Debug

Para ver logs detallados, ejecuta el servidor con:

```bash
python main.py --log-level debug
```

## 🆘 Si el Problema Persiste

1. **Verifica los logs del servidor** para ver si hay errores
2. **Revisa la consola del navegador** para errores específicos de CORS
3. **Prueba con diferentes navegadores** para descartar problemas específicos
4. **Verifica que el túnel de Cloudflare esté funcionando** correctamente

## 📞 Contacto

Si necesitas ayuda adicional, proporciona:
- Logs del servidor
- Errores de la consola del navegador
- URL exacta que está fallando
- Headers de la petición que está fallando 