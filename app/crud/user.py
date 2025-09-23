from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, AdminUserCreate, AdminUserUpdate, UserUpdateProfile
from app.core.security import get_password_hash
from app.core.enums import UserRole

def _normalize_email(email: str) -> str:
    return email.strip().lower()

def _resolve_visitante_role_id(db: Session) -> int:
    role = db.query(Role).filter(Role.name.ilike("visitante")).first()
    return role.id if role else 2

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).options(joinedload(User.role)).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()

def create_public_user(db: Session, user_in: UserCreate) -> User:
    email = _normalize_email(user_in.email)
    hashed_password = get_password_hash(user_in.password)

    role_id = _resolve_visitante_role_id(db)

    user = User(
        email=email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=True,
        role_id=role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_user_by_admin(db: Session, user_in: AdminUserCreate) -> User:
    email = _normalize_email(user_in.email)
    hashed_password = get_password_hash(user_in.password)

    kwargs: dict[str, Any] = {
        "email": email,
        "username": user_in.username,
        "hashed_password": hashed_password,
        "is_active": user_in.is_active if user_in.is_active is not None else True,
    }

    if hasattr(User, "role_id"):
        if isinstance(user_in.role_id, UserRole):
            role_row = db.query(Role).filter(Role.name == user_in.role_id.value).first()
            kwargs["role_id"] = role_row.id if role_row else _resolve_visitante_role_id(db)
        else:
            role_row = db.query(Role).filter(Role.name == str(user_in.role_id)).first()
            if role_row:
                kwargs["role_id"] = role_row.id
            else:
                try:
                    kwargs["role_id"] = int(user_in.role_id)
                except Exception:
                    kwargs["role_id"] = _resolve_visitante_role_id(db)
    else:
        try:
            kwargs["role"] = user_in.role_id or UserRole.VISITANTE
        except Exception:
            kwargs["role"] = UserRole.VISITANTE

    user = User(**kwargs)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user

def update_user_by_admin(db: Session, db_user_to_update: User, user_in: AdminUserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)

    if "email" in update_data:
        update_data["email"] = _normalize_email(update_data["email"])

    if "role" in update_data and update_data["role"] is not None:
        if hasattr(db_user_to_update, "role_id"):
            role_val = update_data["role"]
            if isinstance(role_val, UserRole):
                role_row = db.query(Role).filter(Role.name == role_val.value).first()
                if role_row:
                    db_user_to_update.role_id = role_row.id
            else:
                try:
                    db_user_to_update.role_id = int(role_val)
                except Exception:
                    role_row = db.query(Role).filter(Role.name == str(role_val)).first()
                    if role_row:
                        db_user_to_update.role_id = role_row.id
        else:
            try:
                db_user_to_update.role = update_data["role"]
            except Exception:
                pass
        del update_data["role"]

    for field, value in update_data.items():
        setattr(db_user_to_update, field, value)

    db.add(db_user_to_update)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
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
    if "email" in update_data:
        update_data["email"] = _normalize_email(update_data["email"])
    for field, value in update_data.items():
        setattr(db_user_to_update, field, value)
    db.add(db_user_to_update)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(db_user_to_update)
    return db_user_to_update

def update_password(db: Session, db_user: User, new_password: str) -> User:
    db_user.hashed_password = get_password_hash(new_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
