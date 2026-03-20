from sqlalchemy.orm import Session
from App.Models.UsuarioModel import Usuario
from App.Models.RolModel import RolUsuario 

class UsuarioRepository:
    
    # ==========================================
    # CREATE (Agregar / Insertar)
    # ==========================================
    @staticmethod
    def create_user(db: Session, user_data: dict):
        db_user = Usuario(
            Nombre=user_data.get('nombre'),
            Apellido=user_data.get('apellido'),
            Correo=user_data.get('correo'),  # Usamos 'correo' en lugar de 'email' para que coincida con tu BD
            Contrasena=user_data.get('password'), # ¡Recuerda que ya debe venir hasheada!
            Telefono=user_data.get('telefono'),
            Institucion=user_data.get('institucion')
            # Nota: Según tu diseño, el 'rol' se guarda en la tabla intermedia RolUsuario, 
            # no directamente en la tabla Usuario.
        )
        db.add(db_user)      
        db.commit()          
        db.refresh(db_user)  
        return db_user

    # ==========================================
    #(Ver / Buscar)
    # ==========================================
    @staticmethod
    def get_user_by_email(db: Session, correo: str):
        """Busca un usuario por su correo electrónico (útil para el Login)"""
        return db.query(Usuario).filter(Usuario.Correo == correo).first()

    @staticmethod
    def get_user_by_id(db: Session, id_usuario: str):
        """Busca un usuario por su ID exacto"""
        return db.query(Usuario).filter(Usuario.IdUsuario == id_usuario).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100):
        """Obtiene la lista de todos los usuarios (útil para la tabla de tu Panel Admin)"""
        return db.query(Usuario).offset(skip).limit(limit).all()

    # ==========================================
    # UPDATE (Editar / Actualizar)
    # ==========================================
    @staticmethod
    def update_user(db: Session, id_usuario: str, user_data: dict):
        """Actualiza los datos de un usuario existente"""
        # 1. Buscamos al usuario en la base de datos
        db_user = db.query(Usuario).filter(Usuario.IdUsuario == id_usuario).first()
        
        if not db_user:
            return None # El usuario no existe
            
        # 2. Actualizamos solo los campos que hayan sido enviados en user_data
        if 'nombre' in user_data:
            db_user.Nombre = user_data['nombre']
        if 'apellido' in user_data:
            db_user.Apellido = user_data['apellido']
        if 'correo' in user_data:
            db_user.Correo = user_data['correo']
        if 'telefono' in user_data:
            db_user.Telefono = user_data['telefono']
        if 'institucion' in user_data:
            db_user.Institucion = user_data['institucion']
        if 'password' in user_data: 
            # Solo si el admin decide cambiarle la contraseña
            db_user.Contrasena = user_data['password']

        # 3. Guardamos los cambios
        db.commit()
        db.refresh(db_user)
        return db_user

    # ==========================================
    # DELETE (Eliminar)
    # ==========================================
    @staticmethod
    def delete_user(db: Session, id_usuario: str):
        """Elimina un usuario y sus relaciones de roles de forma segura"""
        try:
            # 1. Buscar al usuario
            db_user = db.query(Usuario).filter(Usuario.IdUsuario == id_usuario).first()
            
            if not db_user:
                return False

            # 2. Borrar primero las entradas en la tabla intermedia (RolUsuario)
            # Esto evita el error de llave foránea y el StaleDataError
            db.query(RolUsuario).filter(RolUsuario.IdUsuario == id_usuario).delete()

            # 3. Borrar al usuario de la tabla principal
            db.delete(db_user)
            
            # 4. Confirmar todos los cambios en una sola transacción
            db.commit()
            return True
            
        except Exception as e:
            # Si algo falla, deshacemos todo para no dejar datos corruptos
            db.rollback()
            print(f"ERROR REPOSITORY: {e}")
            raise e