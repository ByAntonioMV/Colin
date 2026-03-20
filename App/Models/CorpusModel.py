from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from App.Config.DB import Base

class Corpus(Base):
    __tablename__ = "Corpus"

    IdCorpus = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    Nombre = Column(String(255), nullable=False)
    Tipo = Column(String(100))
    Hash = Column(String(64))

    # Relaciones Muchos-a-Muchos
    usuarios = relationship("Usuario", secondary="UsuarioCorpus", back_populates="corpus_asignados")
    lenguas = relationship("Lengua", secondary="CorpusLengua", back_populates="corpus_asociados")


# ==========================================
# TABLA INTERMEDIA (Usuario <-> Corpus)
# ==========================================
class UsuarioCorpus(Base):
    __tablename__ = "UsuarioCorpus"

    IdUsuarioCorpus = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    IdCorpus = Column(String(64), ForeignKey("Corpus.IdCorpus"), nullable=False)
    IdUsuario = Column(String(64), ForeignKey("Usuario.IdUsuario"), nullable=False)