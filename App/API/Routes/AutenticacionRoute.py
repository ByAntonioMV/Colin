from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importamos la configuración de BD y nuestros módulos
from App.Config.DB import get_db
from App.Repositories.UsuarioRepository import UsuarioRepository
from App.Services.AutenticacionService import AutenticacionService

# Creamos el router para agrupar las rutas de autenticación
router = APIRouter(tags=["Autenticación"])

"""
    Endpoint para iniciar sesión. 
    Recibe el correo en 'form_data.username' y la contraseña en 'form_data.password'
"""
@router.post("/api/auth/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    usuario = UsuarioRepository.get_user_by_email(db, correo=form_data.username)
    if not usuario:
        print("DEBUG: Usuario no encontrado en la base de datos")
        raise HTTPException(status_code=401, detail="Correo incorrecto")
    es_valida = AutenticacionService.verify_password(form_data.password, usuario.Contrasena)
    
    if not es_valida:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    # --- NUEVO: Extraer los nombres de los roles ---
    # Como 'usuario.roles' es una lista de objetos Rol, sacamos solo los nombres
    roles_nombres = [rol.Nombre for rol in usuario.roles]

    # 3. Generar el Token JWT con datos extra (Payload)
    # El campo 'sub' sigue siendo el correo (identificador único)
    access_token = AutenticacionService.create_access_token(
        data={
            "sub": usuario.Correo,
            "id": usuario.IdUsuario,
            "nombre": usuario.Nombre,
            "apellido": usuario.Apellido,
            "roles": roles_nombres,
            "institucion": usuario.Institucion
        }
    )
    # 4. Retornar el token
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }