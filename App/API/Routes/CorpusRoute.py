from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from App.Config.DB import get_db
from App.Services.CorpusService import CorpusService
from App.Services.AutenticacionService import AutenticacionService
from App.Services.DatosHadoopService import DatosHadoopService

# Prefijo para todas las rutas de este archivo
router = APIRouter(prefix="/api/corpus", tags=["Corpus"])
stats_service = DatosHadoopService()
# ==========================================
# CREAR CORPUS (BD + HDFS)
# ==========================================
@router.post("/crear")
async def crear_corpus(
    datos: dict, 
    db: Session = Depends(get_db),
    # Protegemos la ruta asumiendo que solo administradores o usuarios validados pueden crear
    current_admin = Depends(AutenticacionService.get_especialista_user) 
):
    """
    Crea un nuevo corpus:
    1. Genera un Hash único.
    2. Crea una carpeta en Hadoop (HDFS).
    3. Guarda los datos (Corpus, Lengua y relación) en MySQL.
    """
    try:
        # Llamamos al servicio (Si tu método en el service no tiene 'async def', lo llamamos sin 'await')
        corpus = CorpusService.crear_nuevo_corpus(db, datos)
        
        return {
            "status": "success",
            "message": f"Corpus '{corpus.Nombre}' creado con éxito",
            "corpus_id": corpus.IdCorpus,
            "hdfs_hash": corpus.Hash # Devolvemos el hash por si el frontend lo necesita
        }
    except Exception as e:
        # Si algo falla en HDFS o en MySQL, devolvemos un error 500 claro al frontend
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el corpus: {str(e)}"
        )

# ==========================================
# LISTAR CORPUS
# ==========================================
@router.get("/listar")
async def listar_corpus(
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_especialista_user)
):
    """Obtiene la lista de todos los corpus para tu tabla HTML"""
    # Aquí asumo que crearás un método 'obtener_todos' en tu CorpusService
    # que llame a CorpusRepository.get_all_corpus(db)
    return CorpusService.obtener_todos(db)

# ==========================================
# ELIMINAR CORPUS
# ==========================================
@router.delete("/eliminar/{id_corpus}")
async def eliminar_corpus(
    id_corpus: str,
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_especialista_user)
):
    """Elimina un corpus por ID y sus relaciones"""
    # De igual forma, asumo que crearás este puente en tu CorpusService
    return await CorpusService.eliminar_corpus(db, id_corpus)

# ==========================================
# SUBIR ARCHIVOS AL CORPUS (HADOOP)
# ==========================================
@router.post("/subir-archivos")
async def subir_archivos(
    # FastAPI es estricto: Form(...) lee texto del FormData y File(...) lee los archivos
    hash_carpeta: str = Form(...),
    archivos: List[UploadFile] = File(...),
    current_admin = Depends(AutenticacionService.get_especialista_user)
):
    """Recibe archivos y los envía a HDFS usando el Hash de la carpeta"""
    # Como nuestro servicio es 'async' (porque usamos await archivo.read()), aquí SÍ lleva 'await'
    return await CorpusService.subir_archivos_hdfs(hash_carpeta, archivos)

# ==============================================
# GRAFICAR CON LOS ARCHIVOS QUE ESTAN EN HADOOP
# ==============================================
@router.get("/graficas/{hash_carpeta}")
async def obtener_graficas(hash_carpeta: str):
    resultado = stats_service.obtener_datos_graficas(hash_carpeta)
    return resultado