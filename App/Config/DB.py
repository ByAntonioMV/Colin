from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://alain:alain117@localhost:3306/TCA"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    future=True,
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()

from App.Models.UsuarioModel import Usuario
from App.Models.RolModel import Rol, RolUsuario
from App.Models.CorpusModel import Corpus, UsuarioCorpus
from App.Models.LenguaModel import Lengua, CorpusLengua

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()