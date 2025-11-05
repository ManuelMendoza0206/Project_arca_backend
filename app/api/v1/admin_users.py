from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user as crud_user
from app.schemas.user import UserOut, AdminUserCreate, AdminUserUpdate
from app.core.dependencies import require_admin_user

#pagination
from fastapi_pagination import Page
from app.schemas.user import UserOutWithRole 
from fastapi_pagination.ext.sqlalchemy import paginate

#auditoria
from app.schemas.audit import AuditLogOut
from app.crud import audit as crud_audit

router = APIRouter(
    dependencies=[Depends(require_admin_user)]  
)

@router.get("/users", response_model=Page[UserOutWithRole], dependencies=[Depends(require_admin_user)])
def admin_list_users(db: Session = Depends(get_db)):
    return paginate(crud_user.get_users_query(db=db))



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


@router.get("/audit-logs", response_model=Page[AuditLogOut], dependencies=[Depends(require_admin_user)],
    summary="Obtener logs de auditoria de autenticacion"
)
def get_audit_logs(db: Session = Depends(get_db)):
    return paginate(crud_audit.get_audit_logs_query(db=db))