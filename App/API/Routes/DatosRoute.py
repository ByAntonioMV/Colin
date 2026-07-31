from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from App.Config.DB import get_db
from App.Services.AutenticacionService import AutenticacionService
from App.Services.DatosHadoopService import DatosHadoopService

router = APIRouter(prefix="/api/datos-hadoop", tags=["Datos Hadoop"])

# ==========================================
# 1. TOKENS
# ==========================================
@router.get("/tokens/{hash_carpeta}")
async def obtener_tabla_tokens(
    hash_carpeta: str,
    db: Session = Depends(get_db),
    current_user = Depends(AutenticacionService.get_especialista_user)
):
    try:
        resultado = DatosHadoopService.obtener_todos_los_tokens(hash_carpeta)

        if resultado["status"] == "error":
            raise HTTPException(status_code=404, detail=resultado["message"])

        return resultado 

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 2. LEMAS
# ==========================================
@router.get("/lemas/{hash_carpeta}")
async def obtener_tabla_lemas(
    hash_carpeta: str,
    db: Session = Depends(get_db),
    current_user = Depends(AutenticacionService.get_especialista_user)
):
    try:
        resultado = DatosHadoopService.obtener_todos_los_lemas(hash_carpeta)

        if resultado["status"] == "error":
            raise HTTPException(status_code=404, detail=resultado["message"])

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 3. GRÁFICAS (CORREGIDO)
# ==========================================
@router.get("/graficas/{hash_carpeta}")
async def obtener_datos_completos_graficas(
    hash_carpeta: str,
    db: Session = Depends(get_db),
    current_user = Depends(AutenticacionService.get_especialista_user)
):
    try:
        resultado = DatosHadoopService.obtener_datos_graficas(hash_carpeta)

        if resultado["status"] == "error":
            raise HTTPException(status_code=404, detail=resultado["message"])

        data = resultado["data"]

        return {
            "status": "success",
            "data": { 
                "kpis": data["kpis"],
                "pos": data["pos"],
                "top_verbos": data["top_verbos"],
                "morfologia": data["morfologia"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 4. KPIs
# ==========================================
@router.get("/resumen-kpis/{hash_carpeta}")
async def obtener_resumen_kpis(
    hash_carpeta: str,
    db: Session = Depends(get_db),
    current_user = Depends(AutenticacionService.get_especialista_user)
):
    try:
        resultado = DatosHadoopService.obtener_datos_graficas(hash_carpeta)

        if resultado["status"] == "error":
            raise HTTPException(status_code=404, detail=resultado["message"])

        return {
            "status": "success",
            "data": {
                "kpis": resultado["data"]["kpis"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/tabla/{hash_corpus}")
def get_tabla_especifica(hash_corpus: str, limite: int = 1000):
    try:
        # Nota: Aquí puedes inyectar/validar tu token de acceso si es necesario
        resultado = DatosHadoopService.obtener_datos_tabla(hash_corpus, limite)
        
        if resultado.get("status") == "error":
            raise HTTPException(status_code=404, detail=resultado["message"])
            
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/nube/{hash_corpus}")
async def get_nube_palabras(
    hash_corpus: str, 
    limite: int = 150,
    db: Session = Depends(get_db),
    current_user = Depends(AutenticacionService.get_especialista_user)
):
    try:
        resultado = DatosHadoopService.obtener_datos_nube(hash_corpus, limite)
        if resultado.get("status") == "error":
            raise HTTPException(status_code=404, detail=resultado["message"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

   
@router.get("/nube/usuario/{hash_corpus}")
async def get_nube_palabras(
    hash_corpus: str, 
    limite: int = 150,
    db: Session = Depends(get_db)
):
    try:
        resultado = DatosHadoopService.obtener_datos_nube(hash_corpus, limite)
        if resultado.get("status") == "error":
            return resultado
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))