from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from App.Config.DB import Base

# ==========================================
# TABLA PRINCIPAL: Lengua
# ==========================================
class Lengua(Base):
    __tablename__ = "Lengua"

    IdLengua = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    Nombre = Column(String(100), nullable=False)
    
    # Se agregaron las nuevas columnas requeridas por tu BD
    Variante = Column(String(100), nullable=False)
    Estado = Column(String(100), nullable=False)
    Municipio = Column(String(100), nullable=False)

    # (Se eliminó la relación hacia la tabla "Variante" porque ya no existe)
    
    # Relación Muchos-a-Muchos (Lengua <-> Corpus)
    corpus_asociados = relationship("Corpus", secondary="CorpusLengua", back_populates="lenguas")


# ==========================================
# TABLA INTERMEDIA (Corpus <-> Lengua)
# ==========================================
class CorpusLengua(Base):
    __tablename__ = "CorpusLengua"

    IdCorpusLengua = Column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    IdCorpus = Column(String(64), ForeignKey("Corpus.IdCorpus"), nullable=False)
    IdLengua = Column(String(64), ForeignKey("Lengua.IdLengua"), nullable=False)