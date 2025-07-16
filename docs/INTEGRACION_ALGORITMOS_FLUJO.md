# 🔄 Integración de Algoritmos en el Flujo de la Aplicación

## 📋 **Resumen**

Los algoritmos de estructuras de datos han sido **integrados directamente en el flujo normal** de la aplicación Cinemax, no como endpoints externos. Cada algoritmo se ejecuta automáticamente en puntos específicos del flujo de datos.

---

## 🎯 **Puntos de Integración**

### **1. 🎬 Películas - QuickSort y Búsqueda Lineal**

#### **Endpoint**: `GET /api/v1/peliculas/`
- **Algoritmo**: QuickSort para ordenar por rating
- **Trigger**: Parámetro `ordenar_por_rating=true`
- **Flujo**: 
  ```
  Usuario solicita películas → MongoDB obtiene datos → QuickSort ordena por rating → Respuesta ordenada
  ```

#### **Endpoint**: `POST /api/v1/peliculas/buscar`
- **Algoritmo**: Búsqueda lineal con filtros múltiples
- **Trigger**: Automático cuando se proporcionan filtros
- **Flujo**:
  ```
  Usuario busca películas → Obtener todas las películas → Búsqueda lineal con filtros → Resultados filtrados
  ```

### **2. 💺 Funciones - Conteo Recursivo de Asientos**

#### **Endpoint**: `GET /api/v1/funciones/{funcion_id}/asientos`
- **Algoritmo**: Conteo recursivo de asientos disponibles
- **Trigger**: Automático en cada consulta
- **Flujo**:
  ```
  Usuario consulta asientos → Crear árbol de sala → Conteo recursivo → Estadísticas con algoritmo usado
  ```

### **3. 💳 Transacciones - HeapSort para Historial**

#### **Endpoint**: `GET /api/v1/transacciones/historial`
- **Algoritmo**: HeapSort para ordenar transacciones por fecha
- **Trigger**: Parámetro `ordenar_por_fecha=true`
- **Flujo**:
  ```
  Usuario solicita historial → Obtener transacciones → HeapSort por fecha → Historial ordenado
  ```

### **4. 📊 Métricas - MergeSort para Salas**

#### **Endpoint**: `GET /api/v1/metricas/ocupacion-salas/todas`
- **Algoritmo**: MergeSort para ordenar salas por ocupación
- **Trigger**: Automático en cada consulta
- **Flujo**:
  ```
  Usuario consulta métricas → Obtener datos de salas → MergeSort por ocupación → Salas ordenadas
  ```

### **5. 📧 Email - Generación Recursiva de QR**

#### **Servicio**: `EmailService._generar_qr_base64()`
- **Algoritmo**: Generación recursiva de QR con reintentos
- **Trigger**: Automático en cada envío de email
- **Flujo**:
  ```
  Transacción completada → Generar QR recursivo → Incluir en email → Enviar confirmación
  ```

---

## 🔧 **Implementación Técnica**

### **Servicio Global de Algoritmos**
```python
# services/global_services.py
algorithms_service = None

def set_algorithms_service(service):
    global algorithms_service
    algorithms_service = service

def get_algorithms_service():
    return algorithms_service
```

### **Inicialización en Main**
```python
# main.py
try:
    from services.algorithms_service import algorithms_service
    set_algorithms_service(algorithms_service)
    print("✅ Servicio de algoritmos inicializado")
except Exception as e:
    print(f"⚠️  No se pudo inicializar algoritmos: {e}")
```

### **Uso en Controladores**
```python
# Ejemplo en peliculas_controller.py
algorithms_service = get_algorithms_service()
if ordenar_por_rating and algorithms_service:
    peliculas = algorithms_service.quicksort_peliculas_rating(peliculas.copy())
```

---

## 📈 **Flujos de Datos con Algoritmos**

### **Flujo 1: Búsqueda de Películas**
```
1. Usuario busca películas con filtros
2. MongoDB obtiene todas las películas activas
3. Algoritmo de búsqueda lineal aplica filtros
4. Resultados filtrados se devuelven al usuario
5. Log: "Búsqueda lineal completada - X resultados"
```

### **Flujo 2: Consulta de Asientos**
```
1. Usuario consulta asientos de una función
2. Redis obtiene asientos ocupados
3. Se crea estructura de árbol de sala
4. Algoritmo recursivo cuenta asientos disponibles
5. Estadísticas incluyen método de conteo usado
```

### **Flujo 3: Historial de Transacciones**
```
1. Usuario solicita historial de compras
2. MongoDB obtiene transacciones del usuario
3. Algoritmo HeapSort ordena por fecha
4. Historial ordenado se devuelve al usuario
5. Log: "Transacciones ordenadas por fecha usando HeapSort"
```

### **Flujo 4: Métricas de Ocupación**
```
1. Usuario consulta métricas de todas las salas
2. MongoDB obtiene datos de funciones
3. Redis obtiene ocupación en tiempo real
4. Algoritmo MergeSort ordena salas por ocupación
5. Métricas ordenadas se devuelven al usuario
```

### **Flujo 5: Generación de QR**
```
1. Transacción se completa exitosamente
2. Sistema genera código QR para entrada
3. Algoritmo recursivo genera QR con reintentos
4. QR se incluye en email de confirmación
5. Email se envía al usuario
```

---

## 🎛️ **Configuración y Control**

### **Parámetros de Control**
- `ordenar_por_rating`: Activa QuickSort en listado de películas
- `ordenar_por_fecha`: Activa HeapSort en historial de transacciones
- Algoritmos recursivos se ejecutan automáticamente

### **Fallbacks**
```python
if algorithms_service:
    # Usar algoritmo
    resultado = algorithms_service.algoritmo(datos)
else:
    # Fallback a método nativo
    resultado = metodo_nativo(datos)
```

### **Logging**
- Cada algoritmo registra su ejecución
- Se incluye información del algoritmo usado en respuestas
- Fallbacks se registran cuando algoritmos no están disponibles

---

## 📊 **Métricas de Rendimiento**

### **Información Incluida en Respuestas**
```json
{
  "peliculas": [...],
  "ordenamiento_aplicado": "quicksort_rating",
  "algoritmo_utilizado": "busqueda_lineal_filtros",
  "algoritmo_conteo": "recursivo",
  "algoritmo_ordenamiento": "mergesort"
}
```

### **Logs de Ejecución**
```
🔄 Aplicando QuickSort para ordenar por rating...
✅ Películas ordenadas por rating usando QuickSort
🔄 Aplicando búsqueda lineal con filtros múltiples...
✅ Búsqueda lineal completada - 5 resultados
🔄 Aplicando conteo recursivo de asientos...
✅ Conteo recursivo completado: 120 asientos disponibles
```

---

## 🔄 **Integración Completa**

### **Estructuras de Datos Utilizadas**
1. **PILAS (Redis)**: Cola de emails y historial de transacciones
2. **COLAS (Redis)**: Procesamiento de pagos y notificaciones
3. **LISTAS ENLAZADAS (MongoDB)**: Navegación de películas y funciones
4. **TABLAS HASH (Redis)**: Cache de sesiones y datos de películas
5. **ÁRBOLES (MongoDB)**: Jerarquía de géneros y estructura de asientos
6. **GRAFOS (MongoDB)**: Relaciones usuario-película y recomendaciones

### **Algoritmos Integrados**
1. **Recursivos**: Búsqueda en árbol, conteo de asientos, generación de QR
2. **Ordenamiento**: QuickSort, MergeSort, HeapSort
3. **Búsqueda**: Binaria, lineal con filtros, DFS, BFS

### **Puntos de Integración**
- ✅ **Películas**: Búsqueda y ordenamiento
- ✅ **Funciones**: Conteo de asientos
- ✅ **Transacciones**: Ordenamiento de historial
- ✅ **Métricas**: Ordenamiento de salas
- ✅ **Email**: Generación de QR

---

## 🚀 **Beneficios de la Integración**

### **1. Transparencia**
- Los algoritmos se ejecutan automáticamente
- Los usuarios no necesitan conocer los algoritmos
- Fallbacks garantizan funcionamiento sin algoritmos

### **2. Rendimiento**
- Algoritmos optimizados para cada caso de uso
- Cache y estructuras de datos eficientes
- Logging para monitoreo de rendimiento

### **3. Escalabilidad**
- Algoritmos se pueden deshabilitar fácilmente
- Nuevos algoritmos se pueden agregar sin cambios en la API
- Configuración flexible por endpoint

### **4. Mantenibilidad**
- Código centralizado en `AlgorithmsService`
- Logs detallados para debugging
- Documentación completa de integración

---

## 📝 **Conclusión**

Los algoritmos de estructuras de datos están **completamente integrados** en el flujo normal de la aplicación Cinemax. Cada algoritmo se ejecuta automáticamente en el punto apropiado del flujo de datos, proporcionando:

- **Mejor rendimiento** en operaciones críticas
- **Transparencia** para el usuario final
- **Flexibilidad** para agregar nuevos algoritmos
- **Robustez** con fallbacks automáticos

La integración es **seamless** y **no requiere cambios** en la interfaz de usuario, manteniendo la funcionalidad existente mientras agrega capacidades algorítmicas avanzadas.

---

*Documentación de integración - Cinemax API v1.0.0* 