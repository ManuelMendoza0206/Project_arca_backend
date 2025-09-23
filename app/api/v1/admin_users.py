from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user as crud_user
from app.schemas.user import UserOut, AdminUserCreate, AdminUserUpdate
from app.core.dependencies import require_admin_user

router = APIRouter(
    dependencies=[Depends(require_admin_user)]  
)

@router.get("/users", response_model=List[UserOut])
def admin_list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_user.get_users(db=db, skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=UserOut)
def admin_get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user

@router.post("/users", response_model=UserOut, status_code=201)
def admin_create_user(user_in: AdminUserCreate, db: Session = Depends(get_db)):
    if crud_user.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    return crud_user.create_user_by_admin(db=db, user_in=user_in)

@router.put("/users/{user_id}", response_model=UserOut)
def admin_update_user(user_id: int, user_in: AdminUserUpdate, db: Session = Depends(get_db)):
    user_db = crud_user.get_user(db, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return crud_user.update_user_by_admin(db=db, db_user_to_update=user_db, user_in=user_in)

@router.delete("/users/{user_id}", response_model=UserOut)
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = crud_user.get_user(db, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return crud_user.delete_user_by_admin(db=db, user_id_to_delete=user_id)
