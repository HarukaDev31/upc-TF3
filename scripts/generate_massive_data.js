// Script para generar datos masivos para pruebas de rendimiento
// Genera: 1000 salas, 50k películas, 1M funciones

// Conectar a la base de datos
db = db.getSiblingDB('cinemax');

print("🎬 Iniciando generación de datos masivos...");

// Configuración de generación
const CONFIG = {
    SALAS_TOTAL: 1000,
    PELICULAS_TOTAL: 50000,
    FUNCIONES_TOTAL: 1000000,
    CLIENTES_TOTAL: 100000,
    TRANSACCIONES_TOTAL: 500000
};

// Arrays de datos para generar contenido realista
const GENEROS = [
    "accion", "aventura", "comedia", "drama", "terror", "ciencia_ficcion",
    "romance", "thriller", "documental", "animacion", "familia", "musical",
    "western", "fantasia", "misterio", "biografico", "guerra", "deportes"
];

const CLASIFICACIONES = ["G", "PG", "PG-13", "R", "NC-17"];

const IDIOMAS = ["español", "inglés", "francés", "alemán", "italiano", "portugués"];

const TIPOS_SALA = ["estandar", "vip", "imax", "4dx", "dolby", "premium"];

const NOMBRES_PELICULAS = [
    "El", "La", "Los", "Las", "Un", "Una", "Mi", "Tu", "Su", "Nuestro",
    "Aventura", "Misterio", "Destino", "Camino", "Viaje", "Sueño", "Realidad",
    "Futuro", "Pasado", "Presente", "Mundo", "Vida", "Muerte", "Amor", "Odio",
    "Guerra", "Paz", "Libertad", "Esclavitud", "Victoria", "Derrota"
];

const APELLIDOS_DIRECTORES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
];

const NOMBRES_DIRECTORES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Thomas", "Christopher", "Charles", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua"
];

// Función para generar ID único
function generateId(prefix, index) {
    return `${prefix}_${String(index).padStart(6, '0')}`;
}

// Función para generar nombre aleatorio
function generateRandomName() {
    const nombres = ["Juan", "María", "Carlos", "Ana", "Luis", "Sofia", "Pedro", "Elena", "Miguel", "Carmen"];
    const apellidos = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"];
    return `${nombres[Math.floor(Math.random() * nombres.length)]} ${apellidos[Math.floor(Math.random() * apellidos.length)]}`;
}

// Función para generar título de película
function generateMovieTitle() {
    const palabras = ["El", "La", "Los", "Las", "Aventura", "Misterio", "Destino", "Camino", "Viaje", "Sueño", "Realidad", "Futuro", "Pasado", "Presente", "Mundo", "Vida", "Muerte", "Amor", "Odio", "Guerra", "Paz", "Libertad", "Esclavitud", "Victoria", "Derrota"];
    const numPalabras = Math.floor(Math.random() * 3) + 2;
    let titulo = "";
    for (let i = 0; i < numPalabras; i++) {
        titulo += palabras[Math.floor(Math.random() * palabras.length)] + " ";
    }
    return titulo.trim();
}

// Función para generar director
function generateDirector() {
    const nombre = NOMBRES_DIRECTORES[Math.floor(Math.random() * NOMBRES_DIRECTORES.length)];
    const apellido = APELLIDOS_DIRECTORES[Math.floor(Math.random() * APELLIDOS_DIRECTORES.length)];
    return `${nombre} ${apellido}`;
}

// Función para generar fecha aleatoria
function generateRandomDate(start, end) {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

// Función para generar asientos
function generateSeats(sala) {
    const asientos = [];
    const filas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'];
    
    for (let i = 0; i < sala.filas; i++) {
        for (let j = 1; j <= sala.asientos_por_fila; j++) {
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

// 1. GENERAR SALAS
print("🏢 Generando " + CONFIG.SALAS_TOTAL + " salas...");

const salas = [];
for (let i = 0; i < CONFIG.SALAS_TOTAL; i++) {
    const tipo = TIPOS_SALA[Math.floor(Math.random() * TIPOS_SALA.length)];
    const capacidad = tipo === "imax" ? 200 : tipo === "vip" ? 100 : Math.floor(Math.random() * 150) + 50;
    const filas = Math.floor(capacidad / 20) + 1;
    const asientos_por_fila = Math.ceil(capacidad / filas);
    
    const sala = {
        id: generateId("sala", i + 1),
        nombre: `Sala ${tipo.toUpperCase()} ${i + 1}`,
        tipo: tipo,
        capacidad_total: capacidad,
        filas: filas,
        asientos_por_fila: asientos_por_fila,
        equipamiento: tipo === "imax" ? ["IMAX", "Dolby Atmos"] : 
                     tipo === "vip" ? ["Butacas reclinables", "Servicio a asiento"] :
                     ["Sonido digital", "Proyección HD"],
        asientos: generateSeats({
            filas: filas,
            asientos_por_fila: asientos_por_fila,
            tipo: tipo
        })
    };
    salas.push(sala);
}

// Insertar salas en una colección separada para referencia
db.salas.insertMany(salas);
print("✅ " + salas.length + " salas generadas");

// 2. GENERAR PELÍCULAS
print("🎬 Generando " + CONFIG.PELICULAS_TOTAL + " películas...");

const peliculas = [];
for (let i = 0; i < CONFIG.PELICULAS_TOTAL; i++) {
    const generos = [];
    const numGeneros = Math.floor(Math.random() * 3) + 1;
    for (let j = 0; j < numGeneros; j++) {
        const genero = GENEROS[Math.floor(Math.random() * GENEROS.length)];
        if (!generos.includes(genero)) {
            generos.push(genero);
        }
    }
    
    const fechaEstreno = generateRandomDate(new Date(2020, 0, 1), new Date(2024, 11, 31));
    const fechaDisponibleHasta = new Date(fechaEstreno.getTime() + Math.random() * 365 * 24 * 60 * 60 * 1000);
    
    const pelicula = {
        _id: generateId("pel", i + 1),
        titulo: generateMovieTitle(),
        titulo_original: generateMovieTitle(),
        sinopsis: "Sinopsis de la película " + (i + 1) + ". Una historia emocionante que cautivará a la audiencia.",
        director: generateDirector(),
        actores_principales: [
            generateRandomName(),
            generateRandomName(),
            generateRandomName()
        ],
        generos: generos,
        duracion_minutos: Math.floor(Math.random() * 180) + 90,
        clasificacion: CLASIFICACIONES[Math.floor(Math.random() * CLASIFICACIONES.length)],
        idioma_original: IDIOMAS[Math.floor(Math.random() * IDIOMAS.length)],
        subtitulos: [IDIOMAS[Math.floor(Math.random() * IDIOMAS.length)]],
        fecha_estreno: fechaEstreno,
        fecha_disponible_desde: fechaEstreno,
        fecha_disponible_hasta: fechaDisponibleHasta,
        poster_url: `https://example.com/posters/pelicula-${i + 1}.jpg`,
        trailer_url: `https://example.com/trailers/pelicula-${i + 1}.mp4`,
        precio_base: Math.floor(Math.random() * 10000) + 8000,
        activa: Math.random() > 0.1, // 90% activas
        created_at: new Date(),
        updated_at: new Date()
    };
    peliculas.push(pelicula);
}

db.peliculas.insertMany(peliculas);
print("✅ " + peliculas.length + " películas generadas");

// 3. GENERAR CLIENTES
print("👥 Generando " + CONFIG.CLIENTES_TOTAL + " clientes...");

const clientes = [];
for (let i = 0; i < CONFIG.CLIENTES_TOTAL; i++) {
    const tipos = ["regular", "frecuente", "premium"];
    const tipo = tipos[Math.floor(Math.random() * tipos.length)];
    
    const cliente = {
        _id: generateId("cliente", i + 1),
        nombre: generateRandomName(),
        email: `cliente${i + 1}@email.com`,
        telefono: `+1${Math.floor(Math.random() * 900000000) + 100000000}`,
        tipo: tipo,
        fecha_registro: generateRandomDate(new Date(2020, 0, 1), new Date()),
        historial_compras: [],
        puntos_acumulados: Math.floor(Math.random() * 1000),
        activo: Math.random() > 0.05 // 95% activos
    };
    clientes.push(cliente);
}

db.clientes.insertMany(clientes);
print("✅ " + clientes.length + " clientes generados");

// 4. GENERAR FUNCIONES
print("🎭 Generando " + CONFIG.FUNCIONES_TOTAL + " funciones...");

const funciones = [];
const batchSize = 10000; // Procesar en lotes para evitar problemas de memoria

for (let i = 0; i < CONFIG.FUNCIONES_TOTAL; i++) {
    const pelicula = peliculas[Math.floor(Math.random() * peliculas.length)];
    const sala = salas[Math.floor(Math.random() * salas.length)];
    
    // Generar fecha de función (próximos 6 meses)
    const fechaInicio = generateRandomDate(new Date(), new Date(Date.now() + 180 * 24 * 60 * 60 * 1000));
    const duracionMinutos = pelicula.duracion_minutos + 30; // +30 min para limpieza
    const fechaFin = new Date(fechaInicio.getTime() + duracionMinutos * 60 * 1000);
    
    const estados = ["programada", "en_venta", "casi_agotada", "agotada", "cancelada"];
    const estado = estados[Math.floor(Math.random() * estados.length)];
    
    const funcion = {
        _id: generateId("fun", i + 1),
        pelicula_id: pelicula._id,
        sala: sala,
        fecha_hora_inicio: fechaInicio,
        fecha_hora_fin: fechaFin,
        precio_base: pelicula.precio_base + Math.floor(Math.random() * 5000),
        precio_vip: pelicula.precio_base + Math.floor(Math.random() * 10000) + 5000,
        estado: estado,
        subtitulos: Math.random() > 0.3,
        idioma_audio: IDIOMAS[Math.floor(Math.random() * IDIOMAS.length)],
        asientos_ocupados: [],
        asientos_reservados: [],
        ventas_totales: Math.floor(Math.random() * sala.capacidad_total * 0.8),
        ingresos_totales: 0,
        created_at: new Date(),
        updated_at: new Date()
    };
    
    funciones.push(funcion);
    
    // Insertar en lotes para evitar problemas de memoria
    if (funciones.length >= batchSize) {
        db.funciones.insertMany(funciones);
        print("✅ Lote de " + funciones.length + " funciones insertado");
        funciones.length = 0; // Limpiar array
    }
}

// Insertar funciones restantes
if (funciones.length > 0) {
    db.funciones.insertMany(funciones);
    print("✅ Lote final de " + funciones.length + " funciones insertado");
}

print("✅ Total de funciones generadas: " + CONFIG.FUNCIONES_TOTAL);

// 5. GENERAR TRANSACCIONES
print("💳 Generando " + CONFIG.TRANSACCIONES_TOTAL + " transacciones...");

const transacciones = [];
const metodosPago = ["tarjeta", "efectivo", "transferencia", "paypal", "criptomonedas"];

for (let i = 0; i < CONFIG.TRANSACCIONES_TOTAL; i++) {
    const cliente = clientes[Math.floor(Math.random() * clientes.length)];
    const funcion = funciones[Math.floor(Math.random() * funciones.length)];
    
    const numAsientos = Math.floor(Math.random() * 4) + 1;
    const asientos = [];
    for (let j = 0; j < numAsientos; j++) {
        const fila = String.fromCharCode(65 + Math.floor(Math.random() * 20)); // A-T
        const numero = Math.floor(Math.random() * 20) + 1;
        asientos.push(fila + numero);
    }
    
    const estados = ["confirmada", "pendiente", "cancelada", "reembolsada"];
    const estado = estados[Math.floor(Math.random() * estados.length)];
    
    const transaccion = {
        _id: generateId("trx", i + 1),
        cliente_id: cliente._id,
        pelicula_id: funcion.pelicula_id,
        funcion_id: funcion._id,
        asientos: asientos,
        metodo_pago: metodosPago[Math.floor(Math.random() * metodosPago.length)],
        monto_total: funcion.precio_base * numAsientos,
        estado: estado,
        numero_factura: `CIN-${String(i + 1).padStart(8, '0')}`,
        fecha_creacion: generateRandomDate(new Date(2023, 0, 1), new Date()),
        fecha_actualizacion: new Date(),
        qr_code: `data:image/png;base64,QR_${i + 1}`,
        detalles_pago: {
            subtotal: funcion.precio_base * numAsientos,
            impuestos: funcion.precio_base * numAsientos * 0.19,
            descuentos: 0,
            total: funcion.precio_base * numAsientos * 1.19
        }
    };
    
    transacciones.push(transaccion);
    
    // Insertar en lotes
    if (transacciones.length >= batchSize) {
        db.transacciones.insertMany(transacciones);
        print("✅ Lote de " + transacciones.length + " transacciones insertado");
        transacciones.length = 0;
    }
}

// Insertar transacciones restantes
if (transacciones.length > 0) {
    db.transacciones.insertMany(transacciones);
    print("✅ Lote final de " + transacciones.length + " transacciones insertado");
}

print("✅ Total de transacciones generadas: " + CONFIG.TRANSACCIONES_TOTAL);

// 6. CREAR ÍNDICES PARA OPTIMIZAR CONSULTAS
print("🔍 Creando índices para optimizar consultas...");

// Índices para películas
db.peliculas.createIndex({ "titulo": "text", "sinopsis": "text" });
db.peliculas.createIndex({ "generos": 1 });
db.peliculas.createIndex({ "fecha_estreno": -1 });
db.peliculas.createIndex({ "activa": 1 });
db.peliculas.createIndex({ "director": 1 });

// Índices para funciones
db.funciones.createIndex({ "pelicula_id": 1 });
db.funciones.createIndex({ "fecha_hora_inicio": 1 });
db.funciones.createIndex({ "estado": 1 });
db.funciones.createIndex({ "sala.id": 1 });

// Índices para transacciones
db.transacciones.createIndex({ "cliente_id": 1 });
db.transacciones.createIndex({ "funcion_id": 1 });
db.transacciones.createIndex({ "estado": 1 });
db.transacciones.createIndex({ "fecha_creacion": -1 });
db.transacciones.createIndex({ "numero_factura": 1 }, { unique: true });

// Índices para clientes
db.clientes.createIndex({ "email": 1 }, { unique: true });
db.clientes.createIndex({ "tipo": 1 });
db.clientes.createIndex({ "activo": 1 });

print("✅ Índices creados exitosamente");

// 7. ESTADÍSTICAS FINALES
print("\n📊 ESTADÍSTICAS FINALES:");
print("================================");
print("🏢 Salas generadas: " + CONFIG.SALAS_TOTAL);
print("🎬 Películas generadas: " + CONFIG.PELICULAS_TOTAL);
print("👥 Clientes generados: " + CONFIG.CLIENTES_TOTAL);
print("🎭 Funciones generadas: " + CONFIG.FUNCIONES_TOTAL);
print("💳 Transacciones generadas: " + CONFIG.TRANSACCIONES_TOTAL);
print("🔍 Índices creados: 15+ índices optimizados");
print("================================");
print("✅ Generación de datos masivos completada exitosamente!");
print("🎬 ¡Tu sistema de cine está listo para pruebas de rendimiento a gran escala!"); 