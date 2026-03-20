from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from App.Repositories.UsuarioRepository import UsuarioRepository
from App.Repositories.RolRepository import RolRepository
from App.Services.AutenticacionService import AutenticacionService
import uuid

class UsuarioService:

    @staticmethod
    async def registrar_nuevo_usuario(db: Session, datos: dict):
        """
        Lógica de negocio para crear un usuario y asignarle su rol.
        """
        # 1. Validar si el correo ya existe en la BD
        usuario_existente = UsuarioRepository.get_user_by_email(db, datos['correo'])
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya se encuentra registrado."
            )

        # 2. Generar Hash de la contraseña (usando tu AutenticacionService)
        # Esto asegura que nunca guardemos texto plano
        password_hasheada = AutenticacionService.get_password_hash(datos['password'])

        # 3. Preparar el objeto para el repositorio de Usuarios
        # Generamos un ID único aquí o dejamos que el Repo lo haga
        user_id = uuid.uuid4().hex
        
        nuevo_user_data = {
            'id_usuario': user_id,
            'nombre': datos['nombre'],
            'apellido': datos['apellido'],
            'correo': datos['correo'],
            'password': password_hasheada,
            'telefono': datos.get('telefono'),
            'institucion': datos.get('institucion')
        }

        try:
            # 4. Guardar en la tabla Usuario
            usuario_creado = UsuarioRepository.create_user(db, nuevo_user_data)

            # 5. Buscar el Rol solicitado y asignarlo
            # El campo 'rol' viene del select de tu HTML
            rol_solicitado = RolRepository.get_rol_by_name(db, datos['rol'])
            
            if not rol_solicitado:
                # Si el rol no existe, podrías asignar uno por defecto o lanzar error
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El rol '{datos['rol']}' no existe en el sistema."
                )

            # 6. Crear la relación en la tabla intermedia RolUsuario
            RolRepository.assign_rol_to_user(
                db, 
                id_usuario=usuario_creado.IdUsuario, 
                id_rol=rol_solicitado.IdRol
            )

            return usuario_creado

        except Exception as e:
            db.rollback() # Si algo falla, deshacemos los cambios
            print(f"Error en UsuarioService: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error al procesar el registro del usuario."
            )
        
    @staticmethod
    async def obtener_todos_los_usuarios(db: Session):
        """Obtiene usuarios y formatea sus roles para el frontend"""
        usuarios = UsuarioRepository.get_all_users(db)
        
        lista_formateada = []
        for u in usuarios:
            lista_formateada.append({
                "id": u.IdUsuario,
                "nombre": u.Nombre,
                "apellido": u.Apellido,
                "correo": u.Correo,
                "telefono": u.Telefono,
                "institucion": u.Institucion,
                # Convertimos la relación de objetos Rol a una lista simple de nombres
                "roles": [rol.Nombre for rol in u.roles]
            })
        return lista_formateada

    # ==========================================
    # NUEVO: Método para Eliminar
    # ==========================================
    @staticmethod
    async def eliminar_usuario(db: Session, id_usuario: str):
        """Elimina un usuario y verifica si existía"""
        exito = UsuarioRepository.delete_user(db, id_usuario)
        if not exito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="El usuario que intenta eliminar no existe."
            )
        return {"message": "Usuario eliminado con éxito"}
    
    @staticmethod
    async def actualizar_usuario(db: Session, id_usuario: str, datos: dict):
        """
        Lógica de negocio para editar un usuario existente.
        """
        # 1. Verificar si el usuario existe
        usuario_db = UsuarioRepository.get_user_by_id(db, id_usuario)
        if not usuario_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # 2. Si se intenta cambiar el correo, verificar que no esté duplicado
        nuevo_correo = datos.get('correo')
        if nuevo_correo and nuevo_correo != usuario_db.Correo:
            if UsuarioRepository.get_user_by_email(db, nuevo_correo):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nuevo correo ya está en uso por otro usuario"
                )

        # 3. Manejo especial de la Contraseña
        # Si el campo password viene vacío o es una cadena de puntos (••••), no la cambiamos
        password_plana = datos.get('password')
        if password_plana and password_plana.strip() != "" and "•" not in password_plana:
            datos['password'] = AutenticacionService.get_password_hash(password_plana)
        else:
            # Eliminamos el password del diccionario para que el Repositorio no lo toque
            if 'password' in datos:
                del datos['password']

        try:
            # 4. Actualizar datos básicos en la tabla Usuario
            usuario_actualizado = UsuarioRepository.update_user(db, id_usuario, datos)

            # 5. Actualizar Rol (si se envió uno)
            nombre_rol = datos.get('rol')
            if nombre_rol:
                rol_db = RolRepository.get_rol_by_name(db, nombre_rol)
                if rol_db:
                    # El repositorio debería tener un método para limpiar roles previos y asignar el nuevo
                    # O simplemente sobreescribir la relación.
                    RolRepository.assign_rol_to_user(db, id_usuario, rol_db.IdRol)

            return usuario_actualizado

        except Exception as e:
            db.rollback()
            print(f"Error al actualizar usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al actualizar el usuario"
            )