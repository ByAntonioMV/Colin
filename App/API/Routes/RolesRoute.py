# App/API/Routes/RolRoute.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from App.Config.DB import get_db
from App.Services.RolesService import RolesService
from App.Services.AutenticacionService import AutenticacionService

# Cambiamos el prefijo para que coincida con tu convención (/api/...)
router = APIRouter(prefix="/api/roles", tags=["Roles"])

@router.post("/crear")
async def crear_rol(
    datos: dict, 
    db: Session = Depends(get_db),
    # Protección de ruta exigiendo que sea administrador
    current_admin = Depends(AutenticacionService.get_admin_user) 
):
    # Llamamos al servicio para la lógica de creación
    rol = await RolesService.crear_rol(db, datos)
    
    return {
        "status": "success",
        "message": f"Rol {rol.Nombre} creado con éxito",
        "rol_id": rol.IdRol
    }

@router.get("/listar")
async def listar_roles(
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_admin_user)
):
    """Obtiene la lista de todos los roles (Solo Admin)"""
    # El Service deberá tener un método obtener_todos_los_roles(db)
    return await RolesService.obtener_todos_los_roles(db)

# --- ELIMINAR ROL ---
@router.delete("/eliminar/{id_rol}")
async def eliminar_rol(
    id_rol: str,
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_admin_user)
):
    """Elimina un rol por ID (Solo Admin)"""
    # El Service valida si existe o si está asignado, lanzando las excepciones necesarias
    return await RolesService.eliminar_rol(db, id_rol)