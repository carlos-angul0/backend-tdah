from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum


# Definición de modelos Pydantic para validación de datos

# Modelo de login
class Login(BaseModel):
    email: EmailStr
    password: str

# Roles controlados
class Rol(str, Enum):
    admin = "admin"
    especialista = "especialista"
    estudiante = "estudiante"

# Crear usuario
class Usuario(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: date
    email: EmailStr
    telefono: str
    rol: Rol
    password: str

# Respuesta segura
class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    apellido: str
    fecha_nacimiento: date
    email: EmailStr
    telefono: str
    rol: Rol
    activo: bool

    class Config:
        from_attributes = True

# Actualizar usuario
class UsuarioUpdate(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: date
    telefono: str
    rol: Rol