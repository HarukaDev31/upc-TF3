// Script de inicialización de MongoDB para el Sistema de Cine
// Este script se ejecuta automáticamente cuando el contenedor de MongoDB se inicia por primera vez

// Crear usuario administrador
db = db.getSiblingDB('admin');
db.createUser({
  user: "admin",
  pwd: "password123",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" }
  ]
});

// Conectar a la base de datos del sistema
db = db.getSiblingDB('cinemax');

// Crear colecciones con índices optimizados
db.createCollection('clientes');
db.createCollection('peliculas');
db.createCollection('funciones');
db.createCollection('transacciones');

// Crear índices para optimizar consultas
db.clientes.createIndex({ "email": 1 }, { unique: true });
db.clientes.createIndex({ "tipo": 1 });
db.clientes.createIndex({ "activo": 1 });

db.peliculas.createIndex({ "titulo": "text", "sinopsis": "text" });
db.peliculas.createIndex({ "generos": 1 });
db.peliculas.createIndex({ "fecha_estreno": -1 });
db.peliculas.createIndex({ "activa": 1 });

db.funciones.createIndex({ "pelicula_id": 1 });
db.funciones.createIndex({ "fecha_hora_inicio": 1 });
db.funciones.createIndex({ "estado": 1 });

db.transacciones.createIndex({ "cliente_id": 1 });
db.transacciones.createIndex({ "funcion_id": 1 });
db.transacciones.createIndex({ "estado": 1 });
db.transacciones.createIndex({ "fecha_creacion": -1 });
db.transacciones.createIndex({ "numero_factura": 1 }, { unique: true });

// Insertar datos de ejemplo

// Clientes de ejemplo
db.clientes.insertMany([
  {
    _id: "cliente_001",
    nombre: "Juan Pérez",
    email: "juan.perez@email.com",
    telefono: "+1234567890",
    tipo: "premium",
    fecha_registro: new Date(),
    historial_compras: [],
    puntos_acumulados: 150,
    activo: true
  },
  {
    _id: "cliente_002",
    nombre: "María García",
    email: "maria.garcia@email.com",
    telefono: "+1234567891",
    tipo: "frecuente",
    fecha_registro: new Date(),
    historial_compras: [],
    puntos_acumulados: 75,
    activo: true
  },
  {
    _id: "cliente_003",
    nombre: "Carlos López",
    email: "carlos.lopez@email.com",
    telefono: "+1234567892",
    tipo: "regular",
    fecha_registro: new Date(),
    historial_compras: [],
    puntos_acumulados: 25,
    activo: true
  }
]);

// Películas de ejemplo
db.peliculas.insertMany([
  {
    _id: "pel_001",
    titulo: "Avengers: Endgame",
    titulo_original: "Avengers: Endgame",
    sinopsis: "Los Vengadores se reúnen una vez más para revertir las acciones de Thanos y restaurar el equilibrio del universo.",
    director: "Anthony Russo, Joe Russo",
    actores_principales: ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo", "Chris Hemsworth"],
    generos: ["accion", "aventura", "ciencia_ficcion"],
    duracion_minutos: 181,
    clasificacion: "PG-13",
    idioma_original: "inglés",
    subtitulos: ["español", "francés"],
    fecha_estreno: new Date("2019-04-26"),
    fecha_disponible_desde: new Date("2019-04-26"),
    fecha_disponible_hasta: new Date("2024-12-31"),
    poster_url: "https://example.com/posters/avengers-endgame.jpg",
    trailer_url: "https://example.com/trailers/avengers-endgame.mp4",
    precio_base: 15000,
    activa: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: "pel_002",
    titulo: "Toy Story 4",
    titulo_original: "Toy Story 4",
    sinopsis: "Woody y sus amigos emprenden una nueva aventura cuando Bonnie trae un nuevo juguete a casa.",
    director: "Josh Cooley",
    actores_principales: ["Tom Hanks", "Tim Allen", "Annie Potts"],
    generos: ["animacion", "familia", "aventura"],
    duracion_minutos: 100,
    clasificacion: "G",
    idioma_original: "inglés",
    subtitulos: ["español", "francés"],
    fecha_estreno: new Date("2019-06-21"),
    fecha_disponible_desde: new Date("2019-06-21"),
    fecha_disponible_hasta: new Date("2024-12-31"),
    poster_url: "https://example.com/posters/toy-story-4.jpg",
    trailer_url: "https://example.com/trailers/toy-story-4.mp4",
    precio_base: 12000,
    activa: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: "pel_003",
    titulo: "Spider-Man: No Way Home",
    titulo_original: "Spider-Man: No Way Home",
    sinopsis: "Peter Parker busca la ayuda del Doctor Strange para hacer que el mundo olvide que es Spider-Man.",
    director: "Jon Watts",
    actores_principales: ["Tom Holland", "Zendaya", "Benedict Cumberbatch"],
    generos: ["accion", "aventura", "ciencia_ficcion"],
    duracion_minutos: 148,
    clasificacion: "PG-13",
    idioma_original: "inglés",
    subtitulos: ["español", "francés"],
    fecha_estreno: new Date("2021-12-17"),
    fecha_disponible_desde: new Date("2021-12-17"),
    fecha_disponible_hasta: new Date("2024-12-31"),
    poster_url: "https://example.com/posters/spider-man-no-way-home.jpg",
    trailer_url: "https://example.com/trailers/spider-man-no-way-home.mp4",
    precio_base: 16000,
    activa: true,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Salas de ejemplo
var salaImax = {
  id: "sala_001",
  nombre: "Sala IMAX",
  tipo: "imax",
  capacidad_total: 200,
  filas: 10,
  asientos_por_fila: 20,
  equipamiento: ["IMAX", "Dolby Atmos", "Butacas reclinables"]
};

var salaVip = {
  id: "sala_002",
  nombre: "Sala VIP",
  tipo: "vip",
  capacidad_total: 100,
  filas: 8,
  asientos_por_fila: 12,
  equipamiento: ["Butacas reclinables", "Servicio a asiento", "Bar premium"]
};

// Generar asientos para las salas
function generarAsientos(sala) {
  var asientos = [];
  var filas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];
  
  for (var i = 0; i < sala.filas; i++) {
    for (var j = 1; j <= sala.asientos_por_fila; j++) {
      asientos.push({
        fila: filas[i],
        numero: j,
        tipo: sala.tipo === "vip" ? "vip" : "estandar",
        precio_adicional: sala.tipo === "vip" ? 5000 : 0
      });
    }
  }
  
  return asientos;
}

salaImax.asientos = generarAsientos(salaImax);
salaVip.asientos = generarAsientos(salaVip);

// Funciones de ejemplo
db.funciones.insertMany([
  {
    _id: "fun_001",
    pelicula_id: "pel_001",
    sala: salaImax,
    fecha_hora_inicio: new Date("2024-12-20T15:30:00"),
    fecha_hora_fin: new Date("2024-12-20T18:30:00"),
    precio_base: 18000,
    precio_vip: 25000,
    estado: "programada",
    subtitulos: true,
    idioma_audio: "español",
    asientos_ocupados: [],
    asientos_reservados: [],
    ventas_totales: 0,
    ingresos_totales: 0,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: "fun_002",
    pelicula_id: "pel_001",
    sala: salaVip,
    fecha_hora_inicio: new Date("2024-12-20T19:00:00"),
    fecha_hora_fin: new Date("2024-12-20T22:00:00"),
    precio_base: 25000,
    precio_vip: 35000,
    estado: "programada",
    subtitulos: false,
    idioma_audio: "español",
    asientos_ocupados: [],
    asientos_reservados: [],
    ventas_totales: 0,
    ingresos_totales: 0,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: "fun_003",
    pelicula_id: "pel_002",
    sala: salaImax,
    fecha_hora_inicio: new Date("2024-12-20T14:00:00"),
    fecha_hora_fin: new Date("2024-12-20T15:40:00"),
    precio_base: 15000,
    precio_vip: 22000,
    estado: "programada",
    subtitulos: true,
    idioma_audio: "español",
    asientos_ocupados: [],
    asientos_reservados: [],
    ventas_totales: 0,
    ingresos_totales: 0,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print("✅ Base de datos inicializada con datos de ejemplo");
print("📊 Colecciones creadas: clientes, peliculas, funciones, transacciones");
print("🎬 Películas agregadas: 3");
print("👥 Clientes agregados: 3");
print("🎭 Funciones programadas: 3");
print("🔍 Índices optimizados para consultas rápidas"); 