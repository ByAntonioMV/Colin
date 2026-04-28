# App/Services/RolService.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from App.Repositories.RolRepository import RolRepository
import uuid

class RolesService:

    @staticmethod
    async def crear_rol(db: Session, datos: dict):
        """
        Lógica de negocio para crear un nuevo rol.
        """
        rol_existente = RolRepository.get_rol_by_name(db, datos['nombre'])
        if rol_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El rol '{datos['nombre']}' ya se encuentra registrado."
            )

        rol_id = uuid.uuid4().hex
        
        nuevo_rol_data = {
            'id_rol': rol_id,
            'nombre': datos['nombre']
        }

        try:
            rol_creado = RolRepository.create_rol(db, nuevo_rol_data)
            return rol_creado
        except Exception as e:
            db.rollback()
            print(f"Error en RolService.crear_rol: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error al procesar la creación del rol."
            )

    # ==========================================
    # NUEVO: Método para Listar todos los roles
    # ==========================================
    @staticmethod
    async def obtener_todos_los_roles(db: Session):
        """
        Obtiene la lista de todos los roles.
        """
        roles = RolRepository.get_all_roles(db)
        
        lista_formateada = []
        for r in roles:
            lista_formateada.append({
                "id": r.IdRol,
                "nombre": r.Nombre
            })
        return lista_formateada

    @staticmethod
    async def eliminar_rol(db: Session, id_rol: str):
        """
        Elimina un rol validando si existe y si no está en uso.
        """
        try:
            exito = RolRepository.delete_rol(db, id_rol)
            
            if not exito:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="El rol que intenta eliminar no existe."
                )
            
            return {"message": "Rol eliminado con éxito"}
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el rol porque está actualmente asignado a uno o más usuarios."
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            print(f"Error en RolService.eliminar_rol: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error interno al intentar eliminar el rol."
            )