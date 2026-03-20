from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(tags=["Vistas"])

# Subir hasta la raíz del proyecto (TCA)
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

@router.get("/")
async def serve_index(): # <- Cambio de nombre aquí
    file_path = os.path.join(PROJECT_ROOT, "Public", "Views", "index.html")
    return FileResponse(file_path)

@router.get("/PanelAdmin")
async def serve_panel_admin(): # <- Cambio de nombre aquí
    file_path = os.path.join(PROJECT_ROOT, "Public", "Views", "PanelAdmin.html")
    return FileResponse(file_path)

@router.get("/PanelCorpus")
async def serve_panel_admin(): # <- Cambio de nombre aquí
    file_path = os.path.join(PROJECT_ROOT, "Public", "Views", "PanelCorpus.html")
    return FileResponse(file_path)

@router.get("/AdministrarCorpus")
async def serve_panel_admin(): # <- Cambio de nombre aquí
    file_path = os.path.join(PROJECT_ROOT, "Public", "Views", "AdministrarCorpus.html")
    return FileResponse(file_path)