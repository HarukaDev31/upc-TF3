# 🚀 Configuración del Servicio WebSocket

## 📋 Resumen

El servicio WebSocket ha sido configurado como un contenedor independiente en Docker Compose para manejar la selección de asientos en tiempo real.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API + WebSocket│    │     Redis       │
│   (Cliente)     │◄──►│   Service       │◄──►│   (Cache)       │
│                 │    │   :8000 + :8001 │    │   :6379         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Iniciar el Servicio

### Opción 1: Solo API + WebSocket (Recomendado para desarrollo)
```bash
# Windows PowerShell
.\scripts\start_websocket.ps1

# Linux/Mac
./scripts/start_websocket.sh
```

### Opción 2: Todos los servicios
```bash
docker-compose up -d
```

## 📊 Verificar Estado

### Health Check
```bash
curl http://localhost:8001/health
```

### Estadísticas
```bash
curl http://localhost:8001/stats
```

### Logs
```bash
docker-compose logs -f websocket
```

## 🧪 Probar el Servicio

### 1. Script de Prueba Completo (Recomendado)
```bash
python test_services.py
```

### 2. Script de Prueba WebSocket Específico
```bash
python test_websocket_service.py
```

### 3. Modo Interactivo
```bash
python test_websocket_service.py interactive
```

### 4. Múltiples Clientes
```bash
python test_websocket_service.py multi
```

### 5. Cliente HTML
Abre `static/websocket_client.html` en tu navegador.

## 🔌 Uso en Frontend

### Conexión Básica
```javascript
const clientId = 'user_' + Date.now();
const ws = new WebSocket(`ws://localhost:8001/ws/${clientId}`);

ws.onopen = () => {
    console.log('Conectado al WebSocket');
    
    // Unirse a una sala
    ws.send(JSON.stringify({
        type: "join_room",
        room_id: "funcion_123"
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Mensaje recibido:', message);
};
```

### Seleccionar Asiento
```javascript
ws.send(JSON.stringify({
    type: "select_seat",
    room_id: "funcion_123",
    seat_id: "A1",
    user_info: {
        name: "Juan Pérez",
        email: "juan@example.com"
    }
}));
```

### Liberar Asiento
```javascript
ws.send(JSON.stringify({
    type: "release_seat",
    room_id: "funcion_123",
    seat_id: "A1"
}));
```

## 📝 Protocolo de Mensajes

### Mensajes de Cliente → Servidor

| Tipo | Descripción | Parámetros |
|------|-------------|------------|
| `join_room` | Unirse a sala | `room_id` |
| `leave_room` | Salir de sala | `room_id` |
| `select_seat` | Seleccionar asiento | `room_id`, `seat_id`, `user_info` |
| `release_seat` | Liberar asiento | `room_id`, `seat_id` |
| `ping` | Keep alive | - |

### Mensajes de Servidor → Cliente

| Tipo | Descripción | Contenido |
|------|-------------|-----------|
| `room_joined` | Confirmación de unión | `room_id`, `client_id` |
| `room_left` | Confirmación de salida | `room_id`, `client_id` |
| `seat_selected` | Asiento seleccionado | `seat_id`, `room_id`, `client_id`, `user_info` |
| `seat_released` | Asiento liberado | `seat_id`, `room_id`, `client_id` |
| `current_selections` | Selecciones actuales | `selections[]` |
| `pong` | Respuesta a ping | `timestamp` |

## 🎨 Ejemplo React

```jsx
import React, { useEffect, useState } from 'react';

const SeatSelection = ({ funcionId }) => {
    const [ws, setWs] = useState(null);
    const [selectedSeats, setSelectedSeats] = useState(new Set());
    const [otherSelections, setOtherSelections] = useState(new Map());

    useEffect(() => {
        const clientId = 'user_' + Date.now();
        const websocket = new WebSocket(`ws://localhost:8001/ws/${clientId}`);
        
        websocket.onopen = () => {
            console.log('Conectado al WebSocket');
            websocket.send(JSON.stringify({
                type: "join_room",
                room_id: funcionId
            }));
        };
        
        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleMessage(message);
        };
        
        setWs(websocket);
        
        return () => {
            websocket.close();
        };
    }, [funcionId]);

    const handleMessage = (message) => {
        switch (message.type) {
            case 'seat_selected':
                if (message.client_id !== ws?.clientId) {
                    setOtherSelections(prev => new Map(prev).set(message.seat_id, message));
                }
                break;
            case 'seat_released':
                if (message.client_id !== ws?.clientId) {
                    setOtherSelections(prev => {
                        const newMap = new Map(prev);
                        newMap.delete(message.seat_id);
                        return newMap;
                    });
                }
                break;
        }
    };

    const selectSeat = (seatId) => {
        if (!ws) return;
        
        ws.send(JSON.stringify({
            type: "select_seat",
            room_id: funcionId,
            seat_id: seatId,
            user_info: {
                name: "Usuario Actual",
                email: "usuario@example.com"
            }
        }));
    };

    return (
        <div className="seat-grid">
            {/* Renderizar grid de asientos */}
        </div>
    );
};
```

## 🎨 Ejemplo Vue.js

```vue
<template>
  <div class="seat-selection">
    <div class="seat-grid">
      <button
        v-for="seat in seats"
        :key="seat.id"
        :class="getSeatClass(seat.id)"
        @click="handleSeatClick(seat.id)"
      >
        {{ seat.id }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ws: null,
      selectedSeats: new Set(),
      otherSelections: new Map()
    };
  },
  mounted() {
    this.connectWebSocket();
  },
  methods: {
    connectWebSocket() {
      const clientId = 'user_' + Date.now();
      this.ws = new WebSocket(`ws://localhost:8001/ws/${clientId}`);
      
      this.ws.onopen = () => {
        this.ws.send(JSON.stringify({
          type: "join_room",
          room_id: this.funcionId
        }));
      };
      
      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      };
    },
    
    handleSeatClick(seatId) {
      if (this.selectedSeats.has(seatId)) {
        this.releaseSeat(seatId);
      } else {
        this.selectSeat(seatId);
      }
    },
    
    selectSeat(seatId) {
      this.ws.send(JSON.stringify({
        type: "select_seat",
        room_id: this.funcionId,
        seat_id: seatId,
        user_info: { name: "Usuario" }
      }));
    },
    
    releaseSeat(seatId) {
      this.ws.send(JSON.stringify({
        type: "release_seat",
        room_id: this.funcionId,
        seat_id: seatId
      }));
    }
  }
};
</script>
```

## 🔧 Configuración

### Variables de Entorno
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123
REDIS_DB=0
WEBSOCKET_PORT=8001
WEBSOCKET_HOST=0.0.0.0
```

### Puertos
- **WebSocket**: 8001
- **Redis**: 6379 (interno), 6380 (externo)

## 🛠️ Troubleshooting

### Problema: Conexión rechazada
```bash
# Verificar que el contenedor esté corriendo
docker-compose ps

# Verificar logs
docker-compose logs websocket

# Verificar puerto
netstat -an | findstr 8001
```

### Problema: Mensajes no llegan
```bash
# Verificar Redis
docker-compose exec redis redis-cli ping

# Verificar health del WebSocket
curl http://localhost:8001/health
```

### Problema: Alto uso de memoria
```bash
# Verificar estadísticas
curl http://localhost:8001/stats

# Reiniciar servicio
docker-compose restart websocket
```

## 📚 Recursos Adicionales

- **Guía Completa**: `WEBSOCKET_GUIDE.md`
- **Prueba Completa**: `test_services.py` (API + WebSocket)
- **Cliente de Prueba WebSocket**: `test_websocket_service.py`
- **Cliente HTML**: `static/websocket_client.html`
- **Scripts**: `scripts/start_websocket.ps1` (Windows) / `scripts/start_websocket.sh` (Linux/Mac)

## 🎯 Próximos Pasos

1. **Integrar con Frontend**: Conectar el WebSocket a tu aplicación React/Vue/Angular
2. **Autenticación**: Implementar JWT para autenticación
3. **Persistencia**: Guardar selecciones finales en MongoDB
4. **Escalabilidad**: Configurar múltiples instancias con load balancer
5. **Monitoreo**: Implementar métricas y alertas

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs: `docker-compose logs -f websocket`
2. Verifica el estado: `curl http://localhost:8001/health`
3. Prueba con el cliente de prueba: `python test_websocket_service.py`
4. Consulta la guía completa: `WEBSOCKET_GUIDE.md` 