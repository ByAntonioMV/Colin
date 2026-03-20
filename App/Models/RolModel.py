from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from App.Config.DB import Base

class Rol(Base):
    __tablename__ = "Rol"

    IdRol = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    Nombre = Column(String(100), nullable=False)

    # Relación inversa a Usuario
    usuarios = relationship("Usuario", secondary="RolUsuario", back_populates="roles")


# ==========================================
# TABLA INTERMEDIA (Asociativa)
# ==========================================
class RolUsuario(Base):
    __tablename__ = "RolUsuario"

    IdRolUsuario = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    IdUsuario = Column(String(64), ForeignKey("Usuario.IdUsuario"), nullable=False)
    IdRol = Column(String(64), ForeignKey("Rol.IdRol"), nullable=False)