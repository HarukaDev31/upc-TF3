  # 📄 Documentación de Endpoints de Compra de Entradas y Transacciones

  ## 1. Comprar Entradas

  **POST** `/api/v1/transacciones/comprar-entrada`

  Compra asientos para una función específica. Solo usuarios autenticados pueden acceder.

  ### Headers
  ```
  Authorization: Bearer <token_jwt>
  Content-Type: application/json
  ```

  ### Body (JSON)
  ```json
  {
    "funcion_id": "fun_001",
    "asientos": ["A1", "A2", "B3"],
    "metodo_pago": "tarjeta_credito",
    "datos_pago": {
      "referencia_externa": "1234567890",
      "ultimos_4_digitos": "1234",
      "banco_emisor": "Banco Ejemplo"
    },
    "codigo_promocion": "CINE2024"
  }
  ```

  - **funcion_id**: ID de la función a comprar.
  - **asientos**: Lista de códigos de asientos a comprar.
  - **metodo_pago**: Uno de: `tarjeta_credito`, `tarjeta_debito`, `efectivo`, `transferencia`, `puntos`.
  - **datos_pago**: (opcional) Información adicional del pago.
  - **codigo_promocion**: (opcional) Código de descuento.

  ### Respuesta Exitosa (200)
  ```json
  {
    "transaccion_id": "TRX_...",
    "numero_factura": "CIN-20240612-XXXXXX",
    "estado": "confirmado",
    "total": 54000,
    "asientos": ["A1", "A2", "B3"],
    "fecha_vencimiento": "2024-06-12T20:00:00Z",
    "resultado_pago": {
      "exitoso": true,
      "codigo_autorizacion": "AUTH...",
      "mensaje": "Pago procesado exitosamente",
      "fecha_procesamiento": "2024-06-12T19:30:00Z"
    },
    "resumen": {
      "id": "TRX_...",
      "numero_factura": "CIN-20240612-XXXXXX",
      "fecha": "2024-06-12T19:30:00Z",
      "cliente_id": "507f1f77bcf86cd799439011",
      "asientos": [
        { "codigo": "A1", "precio": 25000 },
        { "codigo": "A2", "precio": 25000 },
        { "codigo": "B3", "precio": 25000 }
      ],
      "subtotal": 75000,
      "descuentos": 0.1,
      "impuestos": 12825,
      "total": 54000,
      "metodo_pago": "tarjeta_credito",
      "estado": "confirmado"
    }
  }
  ```

  ### Errores
  - `401 Unauthorized`: No autenticado.
  - `404 Not Found`: Usuario o función no encontrada.
  - `409 Conflict`: Uno o más asientos no disponibles.
  - `500 Internal Server Error`: Error interno.

  ---

  ## 2. Historial de Compras

  **GET** `/api/v1/transacciones/historial?limit=20`

  Devuelve el historial de compras del usuario autenticado.

  ### Headers
  ```
  Authorization: Bearer <token_jwt>
  ```

  ### Respuesta Exitosa (200)
  ```json
  {
    "transacciones": [
      {
        "id": "TRX_...",
        "numero_factura": "CIN-20240612-XXXXXX",
        "fecha": "2024-06-12T19:30:00Z",
        "funcion_id": "fun_001",
        "asientos": ["A1", "A2"],
        "total": 50000,
        "estado": "confirmado",
        "metodo_pago": "tarjeta_credito"
      }
      // ...
    ],
    "total": 1
  }
  ```

  ---

  ## 3. Cancelar una Transacción

  **POST** `/api/v1/transacciones/{transaccion_id}/cancelar`

  Cancela una transacción si está pendiente o procesando.

  ### Headers
  ```
  Authorization: Bearer <token_jwt>
  ```

  ### Respuesta Exitosa (200)
  ```json
  {
    "mensaje": "Transacción cancelada exitosamente",
    "transaccion_id": "TRX_...",
    "estado": "cancelado"
  }
  ```

  ### Errores
  - `403 Forbidden`: No tienes permisos para cancelar.
  - `400 Bad Request`: La transacción no puede ser cancelada.
  - `404 Not Found`: Transacción no encontrada.

  ---

  ## 4. Obtener Detalles de una Transacción

  **GET** `/api/v1/transacciones/{transaccion_id}`

  Devuelve los detalles de una transacción específica del usuario autenticado.

  ### Headers
  ```
  Authorization: Bearer <token_jwt>
  ```

  ### Respuesta Exitosa (200)
  ```json
  {
    "id": "TRX_...",
    "numero_factura": "CIN-20240612-XXXXXX",
    "fecha_creacion": "2024-06-12T19:30:00Z",
    "fecha_actualizacion": "2024-06-12T19:30:00Z",
    "estado": "confirmado",
    "funcion_id": "fun_001",
    "pelicula_id": "pel_001",
    "asientos": ["A1", "A2"],
    "subtotal": 50000,
    "descuento_cliente": 0.1,
    "descuento_promocional": 0.05,
    "impuestos": 9500,
    "total": 54000,
    "metodo_pago": "tarjeta_credito",
    "puede_cancelar": false,
    "puede_reembolsar": true,
    "resumen": { ... }
  }
  ```

  ---

  ## 5. Asientos Ocupados de una Función

  **GET** `/api/v1/transacciones/funciones/{funcion_id}/asientos-ocupados`

  Devuelve la lista de asientos ocupados (comprados) para una función.

  ### Respuesta Exitosa (200)
  ```json
  {
    "funcion_id": "fun_001",
    "asientos_ocupados": ["A1", "A2", "B3"],
    "total_ocupados": 3
  }
  ```

  ---

  ## 6. Estadísticas de Ventas (Solo Admin)

  **GET** `/api/v1/transacciones/estadisticas/ventas?fecha_inicio=2024-06-01&fecha_fin=2024-06-12`

  Devuelve estadísticas de ventas en el rango de fechas. Solo para usuarios con email @admin.com.

  ### Headers
  ```
  Authorization: Bearer <token_jwt>
  ```

  ### Respuesta Exitosa (200)
  ```json
  {
    "periodo": {
      "fecha_inicio": "2024-06-01",
      "fecha_fin": "2024-06-12"
    },
    "estadisticas": {
      "total_ventas": 1500000,
      "cantidad_transacciones": 30,
      "cantidad_asientos": 90,
      "promedio_por_transaccion": 50000
    }
  }
  ```

  ---

  ## Notas

  - Todos los endpoints requieren autenticación JWT.
  - Los asientos solo se pueden comprar si están disponibles (ni ocupados ni reservados temporalmente).
  - El pago es simulado, pero la estructura permite integración real.
  - El historial y los detalles solo muestran transacciones del usuario autenticado.
  - El endpoint de estadísticas es solo para administradores. 