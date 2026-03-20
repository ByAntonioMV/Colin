import bcrypt
from App.Config.DB import SessionLocal
from App.Models.UsuarioModel import Usuario
from App.Models.RolModel import Rol, RolUsuario

def rebuild_db():
    db = SessionLocal()
    try:
        # 1. Limpiar datos viejos
        db.query(RolUsuario).delete()
        db.query(Usuario).delete()
        db.query(Rol).delete()
        
        # 2. Crear Roles
        admin_rol = Rol(IdRol="rol-adm", Nombre="Administrador")
        esp_rol = Rol(IdRol="rol-esp", Nombre="Especialista")
        db.add_all([admin_rol, esp_rol])
        
        # 3. Generar Hash REAL (Contraseña: 1234)
        password = "1234"
        salt = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # 4. Crear Usuarios
        alain = Usuario(
            IdUsuario="usr-alain",
            Nombre="Alain",
            Apellido="Admin",
            Correo="alain@correo.com",
            Contrasena=hashed_pwd,
            Institucion="TCA"
        )
        elena = Usuario(
            IdUsuario="usr-elena",
            Nombre="Elena",
            Apellido="Torres",
            Correo="elena@correo.com",
            Contrasena=hashed_pwd,
            Institucion="Investigación"
        )
        db.add_all([alain, elena])
        db.flush() # Para que existan antes de relacionar
        
        # 5. Asignar Roles
        db.add(RolUsuario(IdRolUsuario="rel-1", IdUsuario=alain.IdUsuario, IdRol=admin_rol.IdRol))
        db.add(RolUsuario(IdRolUsuario="rel-2", IdUsuario=elena.IdUsuario, IdRol=esp_rol.IdRol))
        
        db.commit()
        print("✅ Base de datos reconstruida con hashes válidos.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_db()