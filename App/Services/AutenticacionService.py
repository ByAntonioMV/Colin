from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Importamos la conexión y los repositorios
from App.Config.DB import get_db
from App.Repositories.UsuarioRepository import UsuarioRepository
from App.Repositories.RolRepository import RolRepository

# --- CONFIGURACIÓN ---
SECRET_KEY = "super_secreta_clave_tca" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AutenticacionService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compara una contraseña en texto plano con un hash de la base de datos"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            print(f"Error al verificar contraseña: {e}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera un nuevo hash seguro para guardar en la BD"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def create_access_token(data: dict):
        """Crea el JWT incluyendo los datos pasados"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        AUTENTICACIÓN: Verifica que el token sea válido y el usuario exista en BD.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            correo: str = payload.get("sub")
            if correo is None:
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception
        
        usuario = UsuarioRepository.get_user_by_email(db, correo=correo)
        if usuario is None:
            raise credentials_exception
            
        return usuario

    @staticmethod
    async def get_admin_user(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        """
        AUTORIZACIÓN ADMIN: Usa el RolRepository para verificar el rol en tiempo real.
        """
        es_admin = RolRepository.user_has_rol(db, current_user.IdUsuario, "Administrador")
        
        if not es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Se requieren permisos de Administrador"
            )
        
        return current_user

    @staticmethod
    async def get_especialista_user(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        """
        AUTORIZACIÓN ESPECIALISTA: Verifica el rol 'Especialista' en la BD.
        """
        es_especialista = RolRepository.user_has_rol(db, current_user.IdUsuario, "Especialista")
        
        if not es_especialista:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Se requieren permisos de Especialista"
            )
        
        return current_user