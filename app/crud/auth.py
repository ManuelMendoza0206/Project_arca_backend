from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.core.security import verify_password
from app.crud.user import get_user_by_email

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if getattr(user, "is_active", True) is False:
        return None
    return user
