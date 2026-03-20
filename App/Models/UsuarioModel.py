from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid

from App.Config.DB import Base

class Usuario(Base):
    __tablename__ = "Usuario"

    # Se usa default=lambda: uuid.uuid4().hex para generar automáticamente el VARCHAR(64)
    IdUsuario = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    Nombre = Column(String(100), nullable=False)
    Apellido = Column(String(100), nullable=False)
    Correo = Column(String(255), nullable=False, unique=True)
    Contrasena = Column(String(255), nullable=False)
    Telefono = Column(String(20))
    Institucion = Column(String(255))

    # Relaciones Muchos-a-Muchos (Usando strings para evitar importaciones circulares)
    roles = relationship("Rol", secondary="RolUsuario", back_populates="usuarios")
    
    # Esta relación asume que crearás el archivo de Corpus después
    corpus_asignados = relationship("Corpus", secondary="UsuarioCorpus", back_populates="usuarios")