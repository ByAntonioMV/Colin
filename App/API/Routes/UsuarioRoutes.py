from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from App.Config.DB import get_db
from App.Services.UsuariosServices import UsuarioService
from App.Services.AutenticacionService import AutenticacionService

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

@router.post("/crear")
async def crear_usuario(
    datos: dict, 
    db: Session = Depends(get_db),
    # La protección se pone AQUÍ como argumento
    current_admin = Depends(AutenticacionService.get_admin_user) 
):
    # Llamamos al servicio para la lógica de creación
    usuario = await UsuarioService.registrar_nuevo_usuario(db, datos)
    
    return {
        "status": "success",
        "message": f"Usuario {usuario.Nombre} creado con éxito",
        "user_id": usuario.IdUsuario
    }

@router.get("/listar")
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_admin_user)
):
    """Obtiene la lista formateada de todos los usuarios (Solo Admin)"""
    # El Service ya nos devuelve la lista con nombres de roles, sin passwords
    return await UsuarioService.obtener_todos_los_usuarios(db)

@router.put("/actualizar/{id_usuario}")
async def actualizar_usuario(
    id_usuario: str,
    datos: dict, 
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_admin_user)
):
    """
    Endpoint para actualizar un usuario existente.
    Solo accesible por Administradores.
    """
    # Llamamos al servicio que ya tiene la lógica de hasheo y validación de correo
    usuario = await UsuarioService.actualizar_usuario(db, id_usuario, datos)
    
    return {
        "status": "success",
        "message": f"Usuario {usuario.Nombre} actualizado correctamente",
        "user_id": usuario.IdUsuario
    }

# --- ELIMINAR USUARIO ---
@router.delete("/eliminar/{id_usuario}")
async def eliminar_usuario(
    id_usuario: str,
    db: Session = Depends(get_db),
    current_admin = Depends(AutenticacionService.get_admin_user)
):
    """Elimina un usuario por ID (Solo Admin)"""
    # El Service valida si existe y lanza el 404 si no
    return await UsuarioService.eliminar_usuario(db, id_usuario)

