# 🎬 CINEMAX API - Guía de Exposición Ordenada

## 📋 **ESTRUCTURA DE LA PRESENTACIÓN**

### **1. INTRODUCCIÓN (2 minutos)**
### **2. DEMOSTRACIÓN EN VIVO (5 minutos)**
### **3. ARQUITECTURA Y ALGORITMOS (8 minutos)**
### **4. ESTRUCTURAS DE DATOS (5 minutos)**
### **5. MÉTRICAS Y RENDIMIENTO (3 minutos)**
### **6. CONCLUSIONES (2 minutos)**

---

## 🎯 **1. INTRODUCCIÓN**

### **¿Qué es Cinemax API?**
- **Sistema completo de gestión de cine** con API REST
- **Integración transparente de algoritmos** en el flujo normal
- **Arquitectura distribuida** con Docker, MongoDB y Redis
- **15+ algoritmos implementados** (recursivos, ordenamiento, búsqueda)

### **Objetivos del Proyecto**
✅ **Demostrar integración práctica** de algoritmos en aplicaciones reales  
✅ **Implementar estructuras de datos complejas** (árboles, listas,colas,pilas tablas hash)  
✅ **Optimizar rendimiento** con algoritmos eficientes  
✅ **Crear arquitectura escalable** con sistema distribuido  

### **Stack Tecnológico**
```
Backend: FastAPI (Python)
Base de Datos: MongoDB
Cache: Redis
Contenedores: Docker
Tunelización: Cloudflare Tunnel
Autenticación: JWT
```


## 🧮 **3. ARQUITECTURA Y ALGORITMOS**

### **Arquitectura del Sistema**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Cloudflare    │    │   Docker        │
│   (Cliente)     │◄──►│   Tunnel        │◄──►│   Containers    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌────────────────────────────────┼─────────────────┐
                       │                                │                 │
                ┌──────▼──────┐                ┌───────▼──────┐  ┌───────▼──────┐
                │   FastAPI   │                │   MongoDB    │  │    Redis     │
                │   (App)     │                │   (DB)       │  │   (Cache)    │
                └─────────────┘                └──────────────┘  └──────────────┘
```

### **Algoritmos Implementados**

#### **A. Algoritmos Recursivos** 🔄
1. **Búsqueda en Árbol de Géneros** - O(n)
   - **Ubicación:** `services/algorithms_service.py` - `buscar_genero_recursivo()`
   - **Uso:** Búsqueda jerárquica en géneros de películas
2. **Conteo Recursivo de Asientos** - O(n×m)
   - **Ubicación:** `services/algorithms_service.py` - `contar_asientos_disponibles_recursivo()`
   - **Uso:** Contar asientos disponibles en sala
3. **Generación QR Recursiva** - O(1) por intento
   - **Ubicación:** `services/algorithms_service.py` - `generar_qr_recursivo()`
   - **Uso:** Generar códigos QR con reintentos automáticos

#### **B. Algoritmos de Ordenamiento** 📊
1. **QuickSort** - Películas por rating - O(n log n)
   - **Ubicación:** `services/algorithms_service.py` - `quicksort_peliculas_rating()`
   - **Uso:** `controllers/peliculas_controller.py` - Ordenar películas por rating
2. **MergeSort** - Funciones por hora - O(n log n)
   - **Ubicación:** `services/algorithms_service.py` - `mergesort_funciones_hora()`
   - **Uso:** `controllers/funciones_controller.py` - Ordenar funciones cronológicamente
3. **HeapSort** - Transacciones por fecha - O(n log n)
   - **Ubicación:** `services/algorithms_service.py` - `heapsort_transacciones_fecha()`
   - **Uso:** `controllers/transacciones_controller.py` - Ordenar historial de transacciones

#### **C. Algoritmos de Búsqueda** 🔍
1. **Búsqueda Binaria** - Películas ordenadas - O(log n)
   - **Ubicación:** `services/algorithms_service.py` - `busqueda_binaria_peliculas()`
   - **Uso:** Búsqueda rápida en películas ordenadas por título
2. **Búsqueda Lineal** - Con filtros múltiples - O(n×m)
   - **Ubicación:** `services/algorithms_service.py` - `busqueda_lineal_filtros()`
   - **Uso:** `controllers/peliculas_controller.py` - Búsqueda con filtros de género, duración, precio
3. **DFS** - Recomendaciones en grafos - O(V + E)
   - **Ubicación:** `services/algorithms_service.py` - `dfs_recomendaciones()`
   - **Uso:** Sistema de recomendaciones basado en historial de usuario
4. **BFS** - Asientos cercanos - O(V + E)
   - **Ubicación:** `services/algorithms_service.py` - `bfs_asientos_cercanos()`
   - **Uso:** Encontrar asientos disponibles cercanos a uno específico


---

## 🗂️ **4. ESTRUCTURAS DE DATOS**

### **6 Estructuras Implementadas**

#### **1. PILAS (Stacks) - Redis** 📚
- **Cola de emails** - LIFO para prioridad temporal
  - **Ubicación:** `services/email_service.py` - Cola de procesamiento de emails
  - **Operaciones:** LPUSH, RPOP, LLEN
  - **Complejidad:** O(1) para push/pop
  - **Justificación:** Los emails más recientes (confirmaciones, alertas) tienen prioridad sobre los antiguos. LIFO garantiza que emails urgentes se procesen primero, mejorando la experiencia del usuario.

- **Historial de transacciones** - Acceso rápido a transacciones recientes
  - **Ubicación:** `application/use_cases/comprar_entrada_use_case.py` - Historial de usuario
  - **Operaciones:** LPUSH, RPOP, LLEN
  - **Justificación:** Las transacciones más recientes son las más relevantes para el usuario. LIFO permite acceso inmediato a la última compra y facilita operaciones de rollback en orden inverso.

#### **2. COLAS (Queues) - Redis** 📋
- **Procesamiento de pagos** - FIFO para orden cronológico
  - **Ubicación:** `services/payment_service.py` - Cola de pagos pendientes
  - **Operaciones:** LPUSH, RPOP, BLPOP
  - **Complejidad:** O(1) para enqueue/dequeue
  - **Justificación:** FIFO garantiza justicia en el procesamiento de pagos. Todos los pagos se procesan en el orden exacto de llegada, evitando que pagos antiguos se pierdan o se salten, manteniendo la integridad del sistema.

- **Notificaciones WebSocket** - Entrega ordenada de mensajes
  - **Ubicación:** `services/websocket_service.py` - Cola de notificaciones
  - **Operaciones:** LPUSH, RPOP, BLPOP
  - **Justificación:** Las notificaciones deben llegar al usuario en el orden cronológico correcto. FIFO asegura que mensajes importantes (reservas, confirmaciones) lleguen en secuencia, evitando confusión.

#### **3. LISTAS ENLAZADAS - MongoDB** 🔗
- **Lista de películas** - Navegación eficiente
  - **Ubicación:** `controllers/peliculas_controller.py` - Listado con paginación
  - **Operaciones:** Inserción, eliminación, navegación
  - **Complejidad:** O(1) inserción/eliminación
  - **Justificación:** Las películas se agregan y eliminan frecuentemente del catálogo. Las listas enlazadas permiten inserción/eliminación O(1) sin reorganizar toda la estructura, manteniendo la eficiencia en operaciones dinámicas.

- **Funciones por película** - Orden cronológico
  - **Ubicación:** `controllers/funciones_controller.py` - Funciones ordenadas por hora
  - **Operaciones:** Inserción, eliminación, navegación
  - **Justificación:** Las funciones se programan y cancelan constantemente. Las listas enlazadas permiten mantener el orden cronológico sin reindexar, facilitando la navegación secuencial por horarios.

#### **4. TABLAS HASH - Redis** 🗃️
- **Cache de sesiones** - Acceso O(1) por session_id
  - **Ubicación:** `services/auth_service.py` - Gestión de sesiones JWT
  - **Operaciones:** HSET, HGET, HDEL
  - **Complejidad:** O(1) acceso promedio
  - **Justificación:** Las sesiones se consultan en cada request autenticado. Las tablas hash proporcionan acceso O(1) por session_id, reduciendo latencia crítica en autenticación y permitiendo actualizaciones parciales de datos de sesión.

- **Cache de películas** - Datos complejos con actualizaciones parciales
  - **Ubicación:** `controllers/peliculas_controller.py` - Cache de consultas frecuentes
  - **Operaciones:** HSET, HGET, HDEL
  - **Justificación:** Los datos de películas son complejos (título, director, géneros, etc.) y se actualizan parcialmente. Las tablas hash permiten modificar campos específicos sin reescribir todo el objeto, optimizando memoria y rendimiento.

#### **5. ÁRBOLES - MongoDB** 🌳
- **Jerarquía de géneros** - Estructura natural de clasificación
  - **Ubicación:** `services/algorithms_service.py` - `buscar_genero_recursivo()`
  - **Operaciones:** Búsqueda, inserción, eliminación
  - **Complejidad:** O(log n) búsqueda
  - **Justificación:** Los géneros tienen una jerarquía natural (Acción → Superhéroes, Drama → Biográfico). Los árboles reflejan esta estructura, permitiendo búsqueda eficiente O(log n) y navegación intuitiva por subgéneros.

- **Asientos por sala** - Refleja disposición física real
  - **Ubicación:** `services/algorithms_service.py` - `contar_asientos_disponibles_recursivo()`
  - **Operaciones:** Búsqueda, inserción, eliminación
  - **Justificación:** Los asientos en un cine tienen estructura jerárquica natural (Sala → Fila → Asiento). Los árboles modelan esta disposición física, facilitando operaciones como contar asientos disponibles por fila o encontrar asientos adyacentes.

#### **6. GRAFOS - MongoDB** 🕸️
- **Relaciones usuario-película** - Recomendaciones personalizadas
  - **Ubicación:** `services/algorithms_service.py` - `dfs_recomendaciones()`
  - **Operaciones:** DFS, BFS, path finding
  - **Complejidad:** O(V + E) para recorrido
  - **Justificación:** Las relaciones entre usuarios y películas son complejas (vistas, gustos, géneros similares). Los grafos modelan estas conexiones múltiples, permitiendo algoritmos como DFS para encontrar películas recomendadas basadas en patrones de comportamiento.

- **Conexiones por género** - Análisis de patrones
  - **Ubicación:** `application/use_cases/comprar_entrada_use_case.py` - `_actualizar_grafo_recomendaciones()`
  - **Operaciones:** DFS, BFS, path finding
  - **Justificación:** Las películas se conectan por múltiples criterios (género, director, actor). Los grafos capturan estas relaciones complejas, permitiendo análisis de patrones y recomendaciones basadas en similitudes múltiples.

### **🎯 Justificación de Tecnologías por Estructura**

#### **¿Por qué Redis para PILAS y COLAS?**
- **Velocidad extrema:** Operaciones O(1) en memoria
- **Persistencia temporal:** Datos que no necesitan ser permanentes
- **Operaciones atómicas:** Garantizan consistencia en colas concurrentes
- **Expiración automática:** Limpieza automática de datos temporales

#### **¿Por qué MongoDB para LISTAS ENLAZADAS?**
- **Flexibilidad de esquema:** Estructuras que cambian frecuentemente
- **Persistencia permanente:** Datos que deben sobrevivir reinicios
- **Consultas complejas:** Búsquedas por múltiples criterios
- **Escalabilidad horizontal:** Distribución automática de datos

#### **¿Por qué Redis para TABLAS HASH?**
- **Acceso ultra-rápido:** Cache de datos frecuentemente consultados
- **Actualizaciones parciales:** Modificar solo campos específicos
- **Expiración granular:** Control preciso del tiempo de vida
- **Memoria optimizada:** Estructuras compactas en memoria

#### **¿Por qué MongoDB para ÁRBOLES y GRAFOS?**
- **Documentos anidados:** Estructuras jerárquicas naturales
- **Relaciones complejas:** Conexiones múltiples entre entidades
- **Consultas recursivas:** Navegación por estructuras complejas
- **Persistencia de relaciones:** Mantener conexiones a largo plazo

### **🔄 Flujo de Integración de Estructuras y Algoritmos**

#### **Ejemplo: Compra de Entrada Completa**
```
1. Usuario solicita compra
   ↓
2. TABLA HASH (Redis) - Verificar sesión
   ↓
3. LISTA ENLAZADA (MongoDB) - Obtener películas/funciones
   ↓
4. ÁRBOL (MongoDB) - Verificar disponibilidad de asientos
   ↓
5. ALGORITMO RECURSIVO - Contar asientos disponibles
   ↓
6. COLA (Redis) - Procesar pago
   ↓
7. PILA (Redis) - Agregar email a cola
   ↓
8. GRAFO (MongoDB) - Actualizar recomendaciones
   ↓
9. ALGORITMO DFS - Generar recomendaciones
   ↓
10. ALGORITMO QUICKSORT - Ordenar recomendaciones
```

#### **Ejemplo: Búsqueda de Películas**
```
1. Usuario busca películas
   ↓
2. TABLA HASH (Redis) - Verificar cache
   ↓
3. LISTA ENLAZADA (MongoDB) - Obtener todas las películas
   ↓
4. ALGORITMO BÚSQUEDA LINEAL - Aplicar filtros
   ↓
5. ALGORITMO QUICKSORT - Ordenar resultados
   ↓
6. TABLA HASH (Redis) - Guardar en cache
```

---

## 📊 **5. MÉTRICAS Y RENDIMIENTO**

### **Complejidades Algorítmicas**
| Algoritmo | Complejidad Temporal | Complejidad Espacial | Uso |
|-----------|---------------------|---------------------|-----|
| QuickSort | O(n log n) promedio | O(log n) | Ordenar películas por rating |
| MergeSort | O(n log n) | O(n) | Ordenar funciones por hora |
| HeapSort | O(n log n) | O(1) | Ordenar transacciones por fecha |
| Búsqueda Binaria | O(log n) | O(1) | Buscar películas ordenadas |
| Búsqueda Lineal | O(n × m) | O(1) | Buscar con filtros múltiples |
| DFS | O(V + E) | O(V) | Recomendaciones de películas |
| BFS | O(V + E) | O(V) | Asientos cercanos disponibles |



### **Optimizaciones Implementadas**
- **Cache inteligente** con Redis para datos frecuentes
- **Algoritmos adaptativos** que se seleccionan automáticamente
- **Procesamiento paralelo** con múltiples workers
- **Compresión** de respuestas para optimizar ancho de banda

---

## 🎯 **6. CONCLUSIONES**

### **Logros del Proyecto**

#### **✅ Integración Exitosa de Algoritmos**
- **15+ algoritmos** integrados de forma transparente
- **Flujo normal** sin intervención manual requerida
- **Fallbacks inteligentes** para robustez del sistema

#### **✅ Arquitectura Escalable**
- **Sistema distribuido** con contenedores Docker
- **Cache distribuido** con Redis
- **Base de datos** MongoDB para persistencia
- **Tunelización global** con Cloudflare

#### **✅ Optimización de Rendimiento**
- **Estructuras de datos apropiadas** para cada caso de uso
- **Algoritmos eficientes** O(n log n) para ordenamiento
- **Búsqueda optimizada** O(log n) para datos ordenados
- **Cache inteligente** para respuestas rápidas

#### **✅ Funcionalidades Completas**
- **Gestión completa de cine** (películas, funciones, transacciones)
- **Autenticación JWT** segura
- **Emails con QR** generados recursivamente
- **WebSockets** para comunicación en tiempo real

### **Innovación Técnica**
- **Primera implementación** de algoritmos complejos en sistema de cine
- **Integración transparente** sin afectar experiencia del usuario
- **Arquitectura híbrida** que combina múltiples tecnologías
- **Documentación exhaustiva** con ejemplos prácticos

### **Impacto del Proyecto**
- **Demuestra aplicabilidad práctica** de conceptos teóricos
- **Sirve como base** para sistemas más complejos
- **Proporciona framework** para integración de algoritmos
- **Facilita aprendizaje** con ejemplos reales

---

## 🚀 **PUNTOS CLAVE PARA LA EXPOSICIÓN**

### **1. Enfatizar la Integración Transparente**
- Los algoritmos se ejecutan automáticamente
- El usuario no necesita saber qué algoritmo se usa
- El sistema es más eficiente sin cambiar la experiencia

### **2. Mostrar Rendimiento Real**
- Tiempos de respuesta < 200ms
- 1000+ requests/segundo
- Uso eficiente de memoria

### **3. Destacar la Escalabilidad**
- Sistema distribuido con Docker
- Cache distribuido con Redis
- Arquitectura preparada para crecimiento

### **4. Demostrar Funcionalidades Completas**
- Gestión completa de cine
- Autenticación segura
- Emails automáticos con QR
- Comunicación en tiempo real

### **5. Explicar las Estructuras de Datos**
- Cada estructura tiene un propósito específico
- La elección correcta mejora el rendimiento
- Las estructuras trabajan juntas en el sistema

---

## 📝 **NOTAS PARA LA PRESENTACIÓN**

### **Orden de Demostración:**
1. **Mostrar la aplicación funcionando** (endpoints principales)
2. **Explicar la arquitectura** (diagrama visual)
3. **Demostrar algoritmos** (logs y métricas)
4. **Mostrar estructuras de datos** (ejemplos prácticos)
5. **Presentar métricas** (rendimiento real)
6. **Concluir con logros** (impacto del proyecto)

### **Elementos Visuales:**
- **Diagrama de arquitectura** en pantalla
- **Logs en tiempo real** mostrando algoritmos
- **Métricas de rendimiento** actualizadas
- **Ejemplos de código** para algoritmos clave

### **Preguntas Anticipadas:**
- **¿Por qué usar tantos algoritmos?** → Optimización específica para cada caso
- **¿Es realmente escalable?** → Arquitectura distribuida con Docker
- **¿Qué pasa si falla un algoritmo?** → Fallbacks automáticos
- **¿Cómo se mantiene?** → Documentación completa y tests

---

*🎬 Cinemax API - Integración Práctica de Algoritmos en Sistemas Reales* 