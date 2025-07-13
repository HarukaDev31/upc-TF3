"""
Repositorio de Usuario para MongoDB
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from domain.entities.usuario import Usuario, UsuarioCreate, UsuarioResponse
from services.auth_service import auth_service


class UsuarioRepository:
    """Repositorio para operaciones de usuarios"""
    
    def __init__(self, database):
        self.database = database
        self.collection = database.usuarios
    
    async def crear_usuario(self, usuario_data: UsuarioCreate) -> Optional[UsuarioResponse]:
        """Crear un nuevo usuario"""
        try:
            # Verificar si el email ya existe
            existing_user = await self.collection.find_one({"email": usuario_data.email})
            if existing_user:
                return None
            
            # Encriptar password usando el servicio de auth
            password_hash = auth_service.get_password_hash(usuario_data.password)
            
            # Crear documento de usuario
            usuario_doc = {
                "email": usuario_data.email,
                "nombre": usuario_data.nombre,
                "apellido": usuario_data.apellido,
                "telefono": usuario_data.telefono,
                "password_hash": password_hash,
                "fecha_registro": datetime.now(),
                "activo": True
            }
            
            # Insertar en MongoDB
            result = await self.collection.insert_one(usuario_doc)
            
            # Crear respuesta
            usuario_response = UsuarioResponse(
                id=str(result.inserted_id),
                email=usuario_data.email,
                nombre=usuario_data.nombre,
                apellido=usuario_data.apellido,
                telefono=usuario_data.telefono,
                fecha_registro=usuario_doc["fecha_registro"],
                activo=True
            )
            
            return usuario_response
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return None
    
    async def obtener_usuario_por_id(self, usuario_id: str) -> Optional[UsuarioResponse]:
        """Obtener usuario por ID"""
        try:
            usuario_doc = await self.collection.find_one({"_id": ObjectId(usuario_id)})
            if not usuario_doc:
                return None
            
            return UsuarioResponse(
                id=str(usuario_doc["_id"]),
                email=usuario_doc["email"],
                nombre=usuario_doc["nombre"],
                apellido=usuario_doc["apellido"],
                telefono=usuario_doc.get("telefono"),
                fecha_registro=usuario_doc["fecha_registro"],
                activo=usuario_doc["activo"]
            )
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    async def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        """Obtener usuario por email (incluye password_hash para autenticación)"""
        try:
            usuario_doc = await self.collection.find_one({"email": email})
            if not usuario_doc:
                return None
            
            return Usuario(
                id=str(usuario_doc["_id"]),
                email=usuario_doc["email"],
                nombre=usuario_doc["nombre"],
                apellido=usuario_doc["apellido"],
                telefono=usuario_doc.get("telefono"),
                password_hash=usuario_doc.get("password_hash"),
                fecha_registro=usuario_doc["fecha_registro"],
                activo=usuario_doc["activo"]
            )
            
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None
    
    async def autenticar_usuario(self, email: str, password: str) -> Optional[UsuarioResponse]:
        """Autenticar usuario con email y password"""
        try:
            usuario_doc = await self.collection.find_one({"email": email})
            if not usuario_doc:
                return None
            
            # Verificar password usando el servicio de auth
            password_hash = usuario_doc.get("password_hash") or usuario_doc.get("password")
            if not password_hash:
                return None
                
            if auth_service.verify_password(password, password_hash):
                return UsuarioResponse(
                    id=str(usuario_doc["_id"]),
                    email=usuario_doc["email"],
                    nombre=usuario_doc["nombre"],
                    apellido=usuario_doc["apellido"],
                    telefono=usuario_doc.get("telefono"),
                    fecha_registro=usuario_doc["fecha_registro"],
                    activo=usuario_doc["activo"]
                )
            
            return None
            
        except Exception as e:
            print(f"Error autenticando usuario: {e}")
            return None
    
    async def actualizar_usuario(self, usuario_id: str, datos_actualizacion: dict) -> Optional[UsuarioResponse]:
        """Actualizar datos de usuario"""
        try:
            # Remover campos que no se pueden actualizar
            datos_actualizacion.pop("_id", None)
            datos_actualizacion.pop("email", None)  # No permitir cambiar email
            datos_actualizacion.pop("fecha_registro", None)
            
            result = await self.collection.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": datos_actualizacion}
            )
            
            if result.modified_count > 0:
                return await self.obtener_usuario_por_id(usuario_id)
            
            return None
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return None
    
    async def desactivar_usuario(self, usuario_id: str) -> bool:
        """Desactivar usuario"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": {"activo": False}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error desactivando usuario: {e}")
            return False
    
    async def listar_usuarios(self, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """Listar usuarios con paginación"""
        try:
            usuarios = []
            cursor = self.collection.find({"activo": True}).skip(skip).limit(limit)
            
            async for usuario_doc in cursor:
                usuarios.append(UsuarioResponse(
                    id=str(usuario_doc["_id"]),
                    email=usuario_doc["email"],
                    nombre=usuario_doc["nombre"],
                    apellido=usuario_doc["apellido"],
                    telefono=usuario_doc.get("telefono"),
                    fecha_registro=usuario_doc["fecha_registro"],
                    activo=usuario_doc["activo"]
                ))
            
            return usuarios
            
        except Exception as e:
            print(f"Error listando usuarios: {e}")
            return [] 