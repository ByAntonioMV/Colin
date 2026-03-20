from sqlalchemy.orm import Session
from App.Models.CorpusModel import Corpus
from App.Models.LenguaModel import Lengua, CorpusLengua

class CorpusRepository:
    
    # ==========================================
    # CREATE (Múltiples tablas desde un solo formulario)
    # ==========================================
    @staticmethod
    def create_corpus(db: Session, data: dict):
        try:
            # 1. Crear el Corpus
            nuevo_corpus = Corpus(
                Nombre=data.get('nombre'),
                Tipo=data.get('tipo'),
                Hash=data.get('hash', '')
            )
            db.add(nuevo_corpus)
            db.flush() 

            nueva_lengua = Lengua(
                Nombre=data.get('lengua'),
                Variante=data.get('variante'),
                Estado=data.get('estado'),
                Municipio=data.get('municipio')
            )
            db.add(nueva_lengua)
            db.flush() # Genera el IdLengua

            # 3. Vincularlos en la tabla intermedia CorpusLengua
            nueva_relacion = CorpusLengua(
                IdCorpus=nuevo_corpus.IdCorpus,
                IdLengua=nueva_lengua.IdLengua
            )
            db.add(nueva_relacion)

            # 4. Si todo salió bien, guardamos todo junto de forma segura
            db.commit()
            db.refresh(nuevo_corpus)
            
            return nuevo_corpus

        except Exception as e:
            # Si algo falla (ej. faltó un dato), no se guarda nada a medias
            db.rollback()
            print(f"Error al guardar Corpus completo: {e}")
            raise e

    @staticmethod
    def get_all_corpus(db: Session):
        """Obtiene todos los corpus unidos con su respectiva lengua"""
        # Hacemos un JOIN para traer los datos combinados en una sola consulta
        resultados = db.query(
            Corpus.IdCorpus,
            Corpus.Nombre.label("corpus_nombre"),
            Corpus.Tipo,
            Corpus.Hash,
            Lengua.Nombre.label("lengua_nombre"),
            Lengua.Variante,
            Lengua.Estado,
            Lengua.Municipio
        ).join(
            CorpusLengua, Corpus.IdCorpus == CorpusLengua.IdCorpus
        ).join(
            Lengua, CorpusLengua.IdLengua == Lengua.IdLengua
        ).all()
        
        return resultados

    @staticmethod
    def delete_corpus(db: Session, id_corpus: str):
        try:
            # 1. Buscar el corpus
            corpus_a_borrar = db.query(Corpus).filter(Corpus.IdCorpus == id_corpus).first()
            if not corpus_a_borrar:
                return False # No existe
            
            # 2. Borrar las relaciones en la tabla intermedia (CorpusLengua)
            db.query(CorpusLengua).filter(CorpusLengua.IdCorpus == id_corpus).delete()
            
            # 3. Borrar el Corpus
            db.delete(corpus_a_borrar)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar de la BD: {e}")
            raise e
        
    