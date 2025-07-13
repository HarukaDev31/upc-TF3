// Script para limpiar la base de datos antes de generar nuevos datos masivos
// Elimina todas las colecciones y datos existentes

// Conectar a la base de datos
db = db.getSiblingDB('cinemax');

print("🧹 Iniciando limpieza de la base de datos...");

// Lista de colecciones a limpiar
const colecciones = [
    'clientes',
    'peliculas', 
    'funciones',
    'transacciones',
    'salas'
];

// Eliminar cada colección
colecciones.forEach(coleccion => {
    try {
        const count = db[coleccion].countDocuments();
        db[coleccion].drop();
        print(`✅ Colección '${coleccion}' eliminada (${count} documentos)`);
    } catch (error) {
        print(`⚠️  Colección '${coleccion}' no existía o ya fue eliminada`);
    }
});

// Eliminar índices del sistema
try {
    db.system.indexes.drop();
    print("✅ Índices del sistema eliminados");
} catch (error) {
    print("⚠️  No se pudieron eliminar los índices del sistema");
}

// Verificar que la base de datos esté limpia
print("\n📊 Estado de la base de datos después de la limpieza:");
print("================================================================");

colecciones.forEach(coleccion => {
    try {
        const count = db[coleccion].countDocuments();
        print(`${coleccion}: ${count} documentos`);
    } catch (error) {
        print(`${coleccion}: 0 documentos (colección no existe)`);
    }
});

print("================================================================");
print("✅ Limpieza de la base de datos completada exitosamente!");
print("🎬 La base de datos está lista para generar nuevos datos masivos."); 