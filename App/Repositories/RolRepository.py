from sqlalchemy.orm import Session
from App.Models.RolModel import Rol, RolUsuario
from App.Models.UsuarioModel import Usuario

class RolRepository:

    # ==========================================
    # 1. OBTENER (Read)
    # ==========================================
    @staticmethod
    def get_rol_by_id(db: Session, id_rol: str):
        """Busca un rol por su ID"""
        return db.query(Rol).filter(Rol.IdRol == id_rol).first()

    @staticmethod
    def get_rol_by_name(db: Session, nombre_rol: str):
        """Busca un rol por su nombre (ej: 'Administrador')"""
        return db.query(Rol).filter(Rol.Nombre == nombre_rol).first()

    @staticmethod
    def get_all_roles(db: Session):
        """Lista todos los roles disponibles"""
        return db.query(Rol).all()

    # ==========================================
    # 2. CREAR (Create)
    # ==========================================
    @staticmethod
    def create_rol(db: Session, nombre: str):
        """Crea un nuevo tipo de rol en el sistema"""
        nuevo_rol = Rol(Nombre=nombre)
        db.add(nuevo_rol)
        db.commit()
        db.refresh(nuevo_rol)
        return nuevo_rol

    # ==========================================
    # 3. ELIMINAR (Delete)
    # ==========================================
    @staticmethod
    def delete_rol(db: Session, id_rol: str):
        """Elimina un rol (Cuidado: fallará si hay usuarios usándolo)"""
        rol = db.query(Rol).filter(Rol.IdRol == id_rol).first()
        if rol:
            db.delete(rol)
            db.commit()
            return True
        return False

    # ==========================================
    # 4. VERIFICAR ROL DE USUARIO (La "Verdad" de la BD)
    # ==========================================
    @staticmethod
    def user_has_rol(db: Session, id_usuario: str, nombre_rol: str) -> bool:
        """
        Verifica en tiempo real si un usuario tiene un rol específico.
        Hace un JOIN entre Usuario -> RolUsuario -> Rol.
        """
        resultado = db.query(Usuario).join(RolUsuario).join(Rol).filter(
            Usuario.IdUsuario == id_usuario,
            Rol.Nombre == nombre_rol
        ).first()
        
        return resultado is not None

    @staticmethod
    def assign_rol_to_user(db: Session, id_usuario: str, id_rol: str):
        """Asigna un rol existente a un usuario (Crea la relación)"""
        nueva_relacion = RolUsuario(IdUsuario=id_usuario, IdRol=id_rol)
        db.add(nueva_relacion)
        db.commit()
        return nueva_relacion