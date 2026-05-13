from sqlalchemy import Column, Integer, String, Date, Boolean
from .database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    fecha_nacimiento = Column(Date)
    email = Column(String, unique=True, index=True)
    telefono = Column(String)
    rol = Column(String)
    password = Column(String)
    activo = Column(Boolean, default=True)
