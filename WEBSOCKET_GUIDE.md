# Guía de Uso del Servicio WebSocket

## Descripción

El servicio WebSocket permite la selección de asientos en tiempo real para el sistema de cine. Los usuarios pueden seleccionar asientos temporalmente (por 5 minutos) y ver las selecciones de otros usuarios en tiempo real.

## Arquitectura

- **Puerto**: 8001
- **URL Base**: `ws://localhost:8001/ws/{client_id}`
- **Almacenamiento**: Redis para persistencia y sincronización entre instancias
- **Expiración**: Las selecciones expiran automáticamente después de 5 minutos

## Endpoints HTTP

### Health Check
```
GET http://localhost:8001/health
```

### Estadísticas
```
GET http://localhost:8001/stats
```

### Selecciones de una Sala
```
GET http://localhost:8001/room/{room_id}/selections
```

## Protocolo WebSocket

### Conexión
```javascript
const clientId = 'user_' + Date.now(); // ID único del cliente
const ws = new WebSocket(`ws://localhost:8001/ws/${clientId}`);
```

### Tipos de Mensajes

#### 1. Unirse a una Sala
```javascript
ws.send(JSON.stringify({
    type: "join_room",
    room_id: "funcion_123"
}));
```

**Respuesta:**
```json
{
    "type": "room_joined",
    "room_id": "funcion_123",
    "client_id": "user_1234567890"
}
```

#### 2. Salir de una Sala
```javascript
ws.send(JSON.stringify({
    type: "leave_room",
    room_id: "funcion_123"
}));
```

**Respuesta:**
```json
{
    "type": "room_left",
    "room_id": "funcion_123",
    "client_id": "user_1234567890"
}
```

#### 3. Seleccionar Asiento
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

**Respuesta:**
```json
{
    "type": "seat_selected",
    "seat_id": "A1",
    "room_id": "funcion_123",
    "client_id": "user_1234567890"
}
```

#### 4. Liberar Asiento
```javascript
ws.send(JSON.stringify({
    type: "release_seat",
    room_id: "funcion_123",
    seat_id: "A1"
}));
```

**Respuesta:**
```json
{
    "type": "seat_released",
    "seat_id": "A1",
    "room_id": "funcion_123",
    "client_id": "user_1234567890"
}
```

#### 5. Ping/Pong (Keep Alive)
```javascript
ws.send(JSON.stringify({
    type: "ping"
}));
```

**Respuesta:**
```json
{
    "type": "pong",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Mensajes de Broadcast

#### Asiento Seleccionado por Otro Usuario
```json
{
    "type": "seat_selected",
    "seat_id": "B5",
    "room_id": "funcion_123",
    "client_id": "user_9876543210",
    "user_info": {
        "name": "María García",
        "email": "maria@example.com"
    }
}
```

#### Asiento Liberado por Otro Usuario
```json
{
    "type": "seat_released",
    "seat_id": "B5",
    "room_id": "funcion_123",
    "client_id": "user_9876543210"
}
```

#### Selecciones Actuales (al unirse a sala)
```json
{
    "type": "current_selections",
    "selections": [
        {
            "client_id": "user_9876543210",
            "seat_id": "A3",
            "room_id": "funcion_123",
            "user_info": {
                "name": "María García",
                "email": "maria@example.com"
            },
            "timestamp": "2024-01-15T10:25:00.000Z",
            "expires_at": "2024-01-15T10:30:00.000Z"
        }
    ]
}
```

## Implementación en Frontend

### Cliente JavaScript Básico

```javascript
class SeatSelectionClient {
    constructor(serverUrl = 'ws://localhost:8001') {
        this.serverUrl = serverUrl;
        this.clientId = 'user_' + Date.now();
        this.ws = null;
        this.currentRoom = null;
        this.onMessageCallback = null;
        this.onErrorCallback = null;
        this.onCloseCallback = null;
    }

    connect() {
        this.ws = new WebSocket(`${this.serverUrl}/ws/${this.clientId}`);
        
        this.ws.onopen = () => {
            console.log('Conectado al servicio WebSocket');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Mensaje recibido:', message);
            
            if (this.onMessageCallback) {
                this.onMessageCallback(message);
            }
        };

        this.ws.onerror = (error) => {
            console.error('Error en WebSocket:', error);
            if (this.onErrorCallback) {
                this.onErrorCallback(error);
            }
        };

        this.ws.onclose = () => {
            console.log('Conexión WebSocket cerrada');
            if (this.onCloseCallback) {
                this.onCloseCallback();
            }
        };
    }

    joinRoom(roomId) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket no está conectado');
        }

        this.currentRoom = roomId;
        this.ws.send(JSON.stringify({
            type: "join_room",
            room_id: roomId
        }));
    }

    leaveRoom() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.currentRoom) {
            return;
        }

        this.ws.send(JSON.stringify({
            type: "leave_room",
            room_id: this.currentRoom
        }));
        this.currentRoom = null;
    }

    selectSeat(seatId, userInfo = {}) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.currentRoom) {
            throw new Error('WebSocket no está conectado o no hay sala activa');
        }

        this.ws.send(JSON.stringify({
            type: "select_seat",
            room_id: this.currentRoom,
            seat_id: seatId,
            user_info: userInfo
        }));
    }

    releaseSeat(seatId) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.currentRoom) {
            throw new Error('WebSocket no está conectado o no hay sala activa');
        }

        this.ws.send(JSON.stringify({
            type: "release_seat",
            room_id: this.currentRoom,
            seat_id: seatId
        }));
    }

    ping() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        this.ws.send(JSON.stringify({
            type: "ping"
        }));
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }

    setMessageCallback(callback) {
        this.onMessageCallback = callback;
    }

    setErrorCallback(callback) {
        this.onErrorCallback = callback;
    }

    setCloseCallback(callback) {
        this.onCloseCallback = callback;
    }
}
```

### Ejemplo de Uso en React

```jsx
import React, { useEffect, useState } from 'react';

const SeatSelection = ({ funcionId }) => {
    const [client, setClient] = useState(null);
    const [selectedSeats, setSelectedSeats] = useState(new Set());
    const [otherSelections, setOtherSelections] = useState(new Map());
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const seatClient = new SeatSelectionClient();
        
        seatClient.setMessageCallback((message) => {
            switch (message.type) {
                case 'room_joined':
                    console.log('Unido a la sala:', message.room_id);
                    break;
                    
                case 'current_selections':
                    const selectionsMap = new Map();
                    message.selections.forEach(selection => {
                        selectionsMap.set(selection.seat_id, selection);
                    });
                    setOtherSelections(selectionsMap);
                    break;
                    
                case 'seat_selected':
                    if (message.client_id !== seatClient.clientId) {
                        setOtherSelections(prev => new Map(prev).set(message.seat_id, message));
                    }
                    break;
                    
                case 'seat_released':
                    if (message.client_id !== seatClient.clientId) {
                        setOtherSelections(prev => {
                            const newMap = new Map(prev);
                            newMap.delete(message.seat_id);
                            return newMap;
                        });
                    }
                    break;
                    
                case 'seat_selected':
                    if (message.client_id === seatClient.clientId) {
                        setSelectedSeats(prev => new Set(prev).add(message.seat_id));
                    }
                    break;
                    
                case 'seat_released':
                    if (message.client_id === seatClient.clientId) {
                        setSelectedSeats(prev => {
                            const newSet = new Set(prev);
                            newSet.delete(message.seat_id);
                            return newSet;
                        });
                    }
                    break;
            }
        });

        seatClient.setErrorCallback((error) => {
            console.error('Error en WebSocket:', error);
            setIsConnected(false);
        });

        seatClient.setCloseCallback(() => {
            setIsConnected(false);
        });

        seatClient.connect();
        setClient(seatClient);
        setIsConnected(true);

        return () => {
            seatClient.disconnect();
        };
    }, []);

    useEffect(() => {
        if (client && funcionId) {
            client.joinRoom(funcionId);
        }
    }, [client, funcionId]);

    const handleSeatClick = (seatId) => {
        if (!client || !isConnected) return;

        if (selectedSeats.has(seatId)) {
            client.releaseSeat(seatId);
        } else {
            client.selectSeat(seatId, {
                name: "Usuario Actual",
                email: "usuario@example.com"
            });
        }
    };

    const isSeatAvailable = (seatId) => {
        return !selectedSeats.has(seatId) && !otherSelections.has(seatId);
    };

    const isSeatSelectedByMe = (seatId) => {
        return selectedSeats.has(seatId);
    };

    const isSeatSelectedByOther = (seatId) => {
        return otherSelections.has(seatId);
    };

    return (
        <div>
            <div className="connection-status">
                Estado: {isConnected ? 'Conectado' : 'Desconectado'}
            </div>
            
            <div className="seat-grid">
                {/* Renderizar grid de asientos */}
                {Array.from({ length: 10 }, (_, row) => (
                    <div key={row} className="seat-row">
                        {Array.from({ length: 15 }, (_, col) => {
                            const seatId = `${String.fromCharCode(65 + row)}${col + 1}`;
                            const isAvailable = isSeatAvailable(seatId);
                            const isSelected = isSeatSelectedByMe(seatId);
                            const isOtherSelected = isSeatSelectedByOther(seatId);
                            
                            return (
                                <button
                                    key={seatId}
                                    className={`seat ${isSelected ? 'selected' : ''} ${isOtherSelected ? 'other-selected' : ''} ${!isAvailable ? 'unavailable' : ''}`}
                                    onClick={() => handleSeatClick(seatId)}
                                    disabled={!isAvailable && !isSelected}
                                >
                                    {seatId}
                                </button>
                            );
                        })}
                    </div>
                ))}
            </div>
            
            <div className="selected-seats">
                <h3>Mis Selecciones:</h3>
                <ul>
                    {Array.from(selectedSeats).map(seatId => (
                        <li key={seatId}>{seatId}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default SeatSelection;
```

### Ejemplo de Uso en Vue.js

```vue
<template>
  <div class="seat-selection">
    <div class="connection-status">
      Estado: {{ isConnected ? 'Conectado' : 'Desconectado' }}
    </div>
    
    <div class="seat-grid">
      <div v-for="row in 10" :key="row" class="seat-row">
        <button
          v-for="col in 15"
          :key="`${String.fromCharCode(64 + row)}${col}`"
          :class="getSeatClass(`${String.fromCharCode(64 + row)}${col}`)"
          @click="handleSeatClick(`${String.fromCharCode(64 + row)}${col}`)"
          :disabled="!isSeatAvailable(`${String.fromCharCode(64 + row)}${col}`)"
        >
          {{ String.fromCharCode(64 + row) }}{{ col }}
        </button>
      </div>
    </div>
    
    <div class="selected-seats">
      <h3>Mis Selecciones:</h3>
      <ul>
        <li v-for="seat in selectedSeats" :key="seat">{{ seat }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { SeatSelectionClient } from './SeatSelectionClient.js';

export default {
  name: 'SeatSelection',
  props: {
    funcionId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      client: null,
      selectedSeats: new Set(),
      otherSelections: new Map(),
      isConnected: false
    };
  },
  mounted() {
    this.initializeWebSocket();
  },
  beforeUnmount() {
    if (this.client) {
      this.client.disconnect();
    }
  },
  methods: {
    initializeWebSocket() {
      this.client = new SeatSelectionClient();
      
      this.client.setMessageCallback((message) => {
        this.handleWebSocketMessage(message);
      });
      
      this.client.setErrorCallback((error) => {
        console.error('Error en WebSocket:', error);
        this.isConnected = false;
      });
      
      this.client.setCloseCallback(() => {
        this.isConnected = false;
      });
      
      this.client.connect();
      this.isConnected = true;
      
      if (this.funcionId) {
        this.client.joinRoom(this.funcionId);
      }
    },
    
    handleWebSocketMessage(message) {
      switch (message.type) {
        case 'room_joined':
          console.log('Unido a la sala:', message.room_id);
          break;
          
        case 'current_selections':
          const selectionsMap = new Map();
          message.selections.forEach(selection => {
            selectionsMap.set(selection.seat_id, selection);
          });
          this.otherSelections = selectionsMap;
          break;
          
        case 'seat_selected':
          if (message.client_id !== this.client.clientId) {
            this.otherSelections.set(message.seat_id, message);
          }
          break;
          
        case 'seat_released':
          if (message.client_id !== this.client.clientId) {
            this.otherSelections.delete(message.seat_id);
          }
          break;
      }
    },
    
    handleSeatClick(seatId) {
      if (!this.client || !this.isConnected) return;
      
      if (this.selectedSeats.has(seatId)) {
        this.client.releaseSeat(seatId);
        this.selectedSeats.delete(seatId);
      } else {
        this.client.selectSeat(seatId, {
          name: "Usuario Actual",
          email: "usuario@example.com"
        });
        this.selectedSeats.add(seatId);
      }
    },
    
    isSeatAvailable(seatId) {
      return !this.selectedSeats.has(seatId) && !this.otherSelections.has(seatId);
    },
    
    getSeatClass(seatId) {
      const classes = ['seat'];
      
      if (this.selectedSeats.has(seatId)) {
        classes.push('selected');
      } else if (this.otherSelections.has(seatId)) {
        classes.push('other-selected');
      } else if (!this.isSeatAvailable(seatId)) {
        classes.push('unavailable');
      }
      
      return classes.join(' ');
    }
  }
};
</script>

<style scoped>
.seat-selection {
  padding: 20px;
}

.connection-status {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.seat-grid {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 20px;
}

.seat-row {
  display: flex;
  gap: 5px;
  justify-content: center;
}

.seat {
  width: 40px;
  height: 40px;
  border: 1px solid #ccc;
  background-color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.seat:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.seat.selected {
  background-color: #4CAF50;
  color: white;
}

.seat.other-selected {
  background-color: #f44336;
  color: white;
  cursor: not-allowed;
}

.seat.unavailable {
  background-color: #ccc;
  cursor: not-allowed;
}

.selected-seats {
  margin-top: 20px;
}

.selected-seats ul {
  list-style: none;
  padding: 0;
}

.selected-seats li {
  padding: 5px 10px;
  background-color: #e8f5e8;
  margin: 2px 0;
  border-radius: 4px;
}
</style>
```

## Configuración CSS

```css
/* Estilos para el grid de asientos */
.seat-grid {
  display: grid;
  grid-template-columns: repeat(15, 1fr);
  gap: 5px;
  max-width: 800px;
  margin: 0 auto;
}

.seat {
  aspect-ratio: 1;
  border: 2px solid #ddd;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.seat:hover:not(.unavailable) {
  background: #e3f2fd;
  border-color: #2196f3;
}

.seat.selected {
  background: #4caf50;
  color: white;
  border-color: #2e7d32;
}

.seat.other-selected {
  background: #f44336;
  color: white;
  border-color: #c62828;
  cursor: not-allowed;
}

.seat.unavailable {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

/* Indicadores de estado */
.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-connected {
  background: #4caf50;
}

.status-disconnected {
  background: #f44336;
}

.status-connecting {
  background: #ff9800;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
```

## Consideraciones de Producción

### 1. Seguridad
- Implementar autenticación JWT en el WebSocket
- Validar permisos de usuario para acceder a salas
- Sanitizar datos de entrada

### 2. Escalabilidad
- Usar múltiples instancias del servicio WebSocket
- Implementar balanceador de carga
- Usar Redis Cluster para alta disponibilidad

### 3. Monitoreo
- Implementar métricas de conexiones activas
- Monitorear latencia de mensajes
- Alertas para desconexiones masivas

### 4. Manejo de Errores
- Reconexión automática con backoff exponencial
- Manejo de timeouts
- Fallback a polling si WebSocket falla

### 5. Optimización
- Comprimir mensajes grandes
- Implementar heartbeat para detectar conexiones muertas
- Limpiar recursos automáticamente

## Testing

### Cliente de Prueba HTML
```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test Client</title>
    <style>
        .seat { width: 40px; height: 40px; margin: 2px; }
        .selected { background: green; color: white; }
        .other-selected { background: red; color: white; }
    </style>
</head>
<body>
    <div id="app">
        <h2>Cliente de Prueba WebSocket</h2>
        <div id="status">Desconectado</div>
        <button onclick="connect()">Conectar</button>
        <button onclick="disconnect()">Desconectar</button>
        <div id="seats"></div>
        <div id="logs"></div>
    </div>
    
    <script>
        let ws = null;
        let clientId = 'test_' + Date.now();
        
        function connect() {
            ws = new WebSocket(`ws://localhost:8001/ws/${clientId}`);
            
            ws.onopen = () => {
                document.getElementById('status').textContent = 'Conectado';
                log('Conectado al WebSocket');
                
                // Unirse a sala de prueba
                ws.send(JSON.stringify({
                    type: "join_room",
                    room_id: "test_room"
                }));
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                log('Mensaje recibido: ' + JSON.stringify(message));
                handleMessage(message);
            };
            
            ws.onerror = (error) => {
                log('Error: ' + error);
            };
            
            ws.onclose = () => {
                document.getElementById('status').textContent = 'Desconectado';
                log('Desconectado');
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
            }
        }
        
        function handleMessage(message) {
            switch (message.type) {
                case 'room_joined':
                    log('Unido a sala: ' + message.room_id);
                    break;
                case 'seat_selected':
                    updateSeat(message.seat_id, 'selected');
                    break;
                case 'seat_released':
                    updateSeat(message.seat_id, 'available');
                    break;
            }
        }
        
        function selectSeat(seatId) {
            if (!ws) return;
            
            ws.send(JSON.stringify({
                type: "select_seat",
                room_id: "test_room",
                seat_id: seatId,
                user_info: { name: "Test User" }
            }));
        }
        
        function updateSeat(seatId, state) {
            const seat = document.getElementById(`seat_${seatId}`);
            if (seat) {
                seat.className = `seat ${state}`;
            }
        }
        
        function log(message) {
            const logs = document.getElementById('logs');
            logs.innerHTML += '<div>' + new Date().toLocaleTimeString() + ': ' + message + '</div>';
            logs.scrollTop = logs.scrollHeight;
        }
        
        // Crear grid de asientos
        window.onload = function() {
            const seatsDiv = document.getElementById('seats');
            for (let row = 0; row < 5; row++) {
                for (let col = 1; col <= 10; col++) {
                    const seatId = `${String.fromCharCode(65 + row)}${col}`;
                    const seat = document.createElement('button');
                    seat.id = `seat_${seatId}`;
                    seat.className = 'seat';
                    seat.textContent = seatId;
                    seat.onclick = () => selectSeat(seatId);
                    seatsDiv.appendChild(seat);
                }
                seatsDiv.appendChild(document.createElement('br'));
            }
        };
    </script>
</body>
</html>
```

## Comandos de Docker

### Levantar solo el servicio WebSocket
```bash
docker-compose up websocket
```

### Levantar todos los servicios
```bash
docker-compose up -d
```

### Ver logs del WebSocket
```bash
docker-compose logs -f websocket
```

### Reiniciar solo WebSocket
```bash
docker-compose restart websocket
```

### Escalar WebSocket
```bash
docker-compose up -d --scale websocket=3
```

## Troubleshooting

### Problemas Comunes

1. **Conexión rechazada**
   - Verificar que el puerto 8001 esté disponible
   - Verificar que el contenedor esté corriendo: `docker-compose ps`

2. **Mensajes no llegan**
   - Verificar que Redis esté funcionando
   - Revisar logs: `docker-compose logs websocket`

3. **Selecciones no persisten**
   - Verificar conexión a Redis
   - Revisar configuración de Redis en docker-compose.yml

4. **Alto uso de memoria**
   - Verificar limpieza automática de selecciones expiradas
   - Revisar configuración de timeouts

### Logs Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f websocket

# Ver logs de Redis
docker-compose logs -f redis

# Ver estadísticas del WebSocket
curl http://localhost:8001/stats

# Ver salud del servicio
curl http://localhost:8001/health
``` 