from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.session import get_db
from app.crud import user as crud_user
from app.models.user import User
from app.core.enums import UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud_user.get_user_by_email(db, email)
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
    return current_user

def require_admin_user(current_user: User = Depends(get_current_active_user)):
    """"
    role_name = str(getattr(current_user.role, "value", getattr(current_user, "role", ""))).lower()
    if role_name == "administrador" or getattr(current_user, "role_id", None) == 1:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes (admin requerido)")
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes (admin requerido)"
        )
    return current_user
#la logica de lo que es un admin ahora esta en el modelo

ANIMAL_MANAGEMENT_ROLES = {"ADMINISTRADOR", "VETERINARIO", "CUIDADOR"}
TASKS_MANAGEMENT_ROLES = {"ADMINISTRADOR", "CUIDADOR"}

def require_animal_management_permission(current_user: User = Depends(get_current_active_user)):
    if current_user.role.name not in ANIMAL_MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para gestionar animales"
        )
    return current_user

def require_task_management_permission(current_user: User = Depends(get_current_active_user)):
    user_role = str(current_user.role.name if hasattr(current_user.role, 'name') else current_user.role).upper()
    
    if current_user.is_admin:
        return current_user
        
    if user_role not in TASKS_MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para realizar esta accion"
        )
    return current_user