from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status
from typing import List, Optional

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, AdminUserCreate, AdminUserUpdate, UserUpdateProfile
from app.core.security import get_password_hash
from app.core.enums import UserRole

def _get_visitante_role_id(db: Session) -> int:

    role = db.query(Role).filter(Role.name == UserRole.VISITANTE.value).first()
    if not role:
        raise RuntimeError(f"Rol por defecto '{UserRole.VISITANTE.value}' no encontrado en la base de datos")
    return role.id

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID
    """
    return db.query(User).options(
        joinedload(User.role)
    ).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Busca un usuario por su email, aplicando la misma normalizacion
    """
    normalized_email = email.strip().lower()
    return db.query(User).options(
        joinedload(User.role)
    ).filter(User.email == normalized_email).first()

def get_users_query(db: Session) -> Query:
    return db.query(User).options(
        joinedload(User.role)
    ).order_by(User.id)

def create_public_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    role_id = _get_visitante_role_id(db)

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=True,
        role_id=role_id
    )
    
    db.add(user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email o nombre de usuario ya existen: {e.orig}"
        )
    db.refresh(user)
    return user

def create_user_by_admin(db: Session, user_in: AdminUserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=user_in.is_active,
        role_id=user_in.role_id 
    )
    
    db.add(user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email o nombre de usuario ya existen: {e.orig}"
        )
    db.refresh(user)
    return user

def update_user_by_admin(db: Session, db_user_to_update: User, user_in: AdminUserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user_to_update, field, value)

    db.add(db_user_to_update)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto de datos: {e.orig}"
        )
    db.refresh(db_user_to_update)
    return db_user_to_update

def delete_user_by_admin(db: Session, user_id_to_delete: int) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id_to_delete).first()
    if not db_user:
        return None
    
    db.delete(db_user)
    db.commit()
    return db_user

def update_own_profile(db: Session, db_user_to_update: User, user_in: UserUpdateProfile) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user_to_update, field, value)
        
    db.add(db_user_to_update)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto de datos: {e.orig}"
        )
    db.refresh(db_user_to_update)
    return db_user_to_update

def update_password(db: Session, db_user: User, new_password: str) -> User:
    db_user.hashed_password = get_password_hash(new_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user