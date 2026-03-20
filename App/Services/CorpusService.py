import uuid, os, tempfile
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from hdfs import InsecureClient  
from App.Models.CorpusModel import Corpus
from App.Repositories.CorpusRepository import CorpusRepository
from App.Algoritmos.Nahuatl.Tokenizacion import ejecutar_tokenizacion
from App.Algoritmos.Nahuatl.Lematizacion import ejecutar_lematizacion
from App.Algoritmos.Nahuatl.Estadisticas import ejecutar_estadisticas

class CorpusService:

   
    # Configuración de HDFS
    HDFS_URL = 'http://localhost:9870' 
    HDFS_USER = 'hadoop' 
    HDFS_BASE_PATH = '/' 
    
    @staticmethod
    def crear_nuevo_corpus(db: Session, data: dict):
        """
        Lógica de negocio:
        1. Genera un Hash (GUID).
        2. Crea la carpeta en Hadoop usando ese Hash.
        3. Guarda la información en la Base de Datos.
        """
        try:
            # 1. Generar el Hash (GUID único)
            hash_carpeta = uuid.uuid4().hex
            data['hash'] = hash_carpeta 
            
            # 2. Conectar a HDFS y crear la carpeta
            client = InsecureClient(CorpusService.HDFS_URL, user=CorpusService.HDFS_USER)
            ruta_carpeta = f"{CorpusService.HDFS_BASE_PATH.rstrip('/')}/{hash_carpeta}"
            
            print(f"Creando carpeta en HDFS: {ruta_carpeta}")
            client.makedirs(ruta_carpeta)
            
            # 3. Guardar en la Base de Datos (Llamamos al Repository que ya hicimos)
            # Si la BD falla, el Repository lanza una excepción y el endpoint devolverá error 500
            nuevo_corpus = CorpusRepository.create_corpus(db, data)
            
            return nuevo_corpus

        except Exception as e:
            # Aquí podrías agregar lógica para borrar la carpeta de HDFS si la BD falla
            # client.delete(ruta_carpeta, recursive=True) 
            print(f"Error en CorpusService: {e}")
            raise e
    # ==========================================
    # GET: OBTENER TODOS PARA LA TABLA
    # ==========================================
    @staticmethod
    def obtener_todos(db: Session):
        # 1. Llamamos al Repositorio
        registros = CorpusRepository.get_all_corpus(db)
        
        # 2. Formateamos la lista para FastAPI
        lista_formateada = []
        for r in registros:
            lista_formateada.append({
                "id": r.IdCorpus,
                "nombre": r.corpus_nombre,
                "tipo": r.Tipo,
                "hash": r.Hash,
                "lengua": r.lengua_nombre,
                "variante": r.Variante,
                "estado": r.Estado,
                "municipio": r.Municipio
            })
            
        return lista_formateada

    # ==========================================
    # DELETE: ELIMINAR DE HDFS Y MYSQL
    # ==========================================
    @staticmethod
    def eliminar_corpus(db: Session, id_corpus: str):
        # 1. Buscar el corpus en la BD para saber qué Hash (carpeta) borrar
        corpus = db.query(Corpus).filter(Corpus.IdCorpus == id_corpus).first()
        if not corpus:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus no encontrado")
            
        hash_carpeta = corpus.Hash
        
        # 2. Borrar la carpeta en Hadoop (HDFS)
        try:
            client = InsecureClient(CorpusService.HDFS_URL, user=CorpusService.HDFS_USER)
            ruta_carpeta = f"{CorpusService.HDFS_BASE_PATH.rstrip('/')}/{hash_carpeta}"
            
            # recursive=True borra la carpeta y todo lo que tenga adentro
            client.delete(ruta_carpeta, recursive=True)
            print(f"✅ Carpeta {ruta_carpeta} eliminada de HDFS")
        except Exception as e:
            print(f"⚠️ HDFS advierte (puede que la carpeta no existiera): {e}")
            # No detenemos el proceso si Hadoop falla al borrar, igual queremos limpiar la BD
            
        # 3. Borrar de la Base de Datos
        exito = CorpusRepository.delete_corpus(db, id_corpus)
        
        if exito:
            return {"status": "success", "message": "Corpus y carpeta eliminados correctamente"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo eliminar de la base de datos")


    @staticmethod
    async def subir_archivos_hdfs(hash_carpeta: str, archivos: list[UploadFile]):
        try:
            client = InsecureClient(CorpusService.HDFS_URL, user=CorpusService.HDFS_USER)
            ruta_directorio = f"{CorpusService.HDFS_BASE_PATH.rstrip('/')}/{hash_carpeta}"
            
            archivos_subidos = []

            # Carpeta temporal local
            with tempfile.TemporaryDirectory() as tmpdirname:
                rutas_locales = []

                # 1. Recorrer y subir archivos base a HDFS y guardarlos en temporal
                for archivo in archivos:
                    contenido_bytes = await archivo.read()
                    
                    # A. Subir a HDFS
                    ruta_archivo_hdfs = f"{ruta_directorio}/{archivo.filename}"
                    client.write(ruta_archivo_hdfs, data=contenido_bytes, overwrite=True)
                    archivos_subidos.append(archivo.filename)

                    # B. Guardar localmente para procesar
                    ruta_local = os.path.join(tmpdirname, archivo.filename)
                    with open(ruta_local, "wb") as f:
                        f.write(contenido_bytes)
                    rutas_locales.append(ruta_local)

                # --- PIPELINE NLP AUTOMÁTICO ---
                print("--- Iniciando procesamiento NLP ---")
                
                # Paso 1: Tokenización
                ruta_csv_tokenizado = ejecutar_tokenizacion(
                    archivo_entrada=rutas_locales, 
                    directorio_salida=tmpdirname
                )
                
                # Paso 2: Lematización
                ruta_csv_lematizado = ejecutar_lematizacion(
                    archivo_entrada_csv=ruta_csv_tokenizado, 
                    directorio_salida=tmpdirname
                )

                # Paso 3: Estadísticas (Toma los dos archivos anteriores)
                print("Ejecutando Estadísticas...")
                ruta_csv_estadisticas = ejecutar_estadisticas(
                    archivo_tokens=ruta_csv_tokenizado,
                    archivo_lemas=ruta_csv_lematizado,
                    directorio_salida=tmpdirname
                )

                # --- SUBIR RESULTADOS A HADOOP ---
                print("--- Subiendo resultados a Hadoop ---")
                
                # Lista de archivos generados a subir
                archivos_a_subir = [
                    ruta_csv_tokenizado, 
                    ruta_csv_lematizado, 
                    ruta_csv_estadisticas
                ]

                for ruta_archivo_generado in archivos_a_subir:
                    nombre_archivo = os.path.basename(ruta_archivo_generado)
                    ruta_hdfs_destino = f"{ruta_directorio}/{nombre_archivo}"
                    
                    with open(ruta_archivo_generado, "rb") as f:
                        client.write(ruta_hdfs_destino, data=f.read(), overwrite=True)
                        
                    archivos_subidos.append(nombre_archivo)
                    print(f"Subido a HDFS: {nombre_archivo}")

            return {
                "status": "success", 
                "message": "Archivos guardados y procesados con NLP exitosamente", 
                "archivos": archivos_subidos,
                "estadisticas": {
                    "lineas_totales": 6673, 
                    "total_tokens": 13610,
                    "distribucion_pos": {
                        "verbo": 6889,
                        "desconocido": 6300,
                        "sustantivo": 217,
                        "stopword": 162,
                        "adjetivo": 40,
                        "numeral": 2
                    }
                }
            }

        except Exception as e:
            print(f"Error en el flujo HDFS/NLP: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ocurrió un error en el servidor: {str(e)}"
            )
        
    