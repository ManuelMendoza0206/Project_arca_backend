from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import LoginRequest, TokenResponse, TokenRefreshRequest
from app.crud import user as crud_user
from app.crud import token as crud_token
from app.core.security import create_access_token, create_refresh_token
from app.crud.auth import authenticate_user
from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.models.user import User
router = APIRouter()


def _get_role_claim(user: User) -> str | None:
    if user.role:
        return user.role.name
    return None

def _issue_tokens_for_user(user, db: Session):
    extra_claims = {"role": _get_role_claim(user)} if _get_role_claim(user) else None
    access_token = create_access_token(subject=user.email, extra_claims=extra_claims)

    rt = create_refresh_token(subject=user.email)
    crud_token.create_refresh_token_record(
        db, user_id=user.id, jti=rt["jti"], expires_at=rt["expires_at"], device_info=rt.get("device_info")
    )

    return access_token, rt["token"]
#crud_user.create_public_user ya maneja IntegrityError y lanza un HTTPException 409
@router.post("/register", response_model=UserOut, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    #if crud_user.get_user_by_email(db, user_in.email):
    #    raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud_user.create_public_user(db=db, user_in=user_in)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")

    access_token, refresh_token = _issue_tokens_for_user(user, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Token nvalido")
        jti, sub = decoded.get("jti"), decoded.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token invalido")

    if not crud_token.is_refresh_token_valid(db, jti):
        raise HTTPException(status_code=401, detail="Refresh token invalido o revocado")

    crud_token.revoke_refresh_token_by_jti(db, jti)

    user = crud_user.get_user_by_email(db, sub)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    access_token, refresh_token = _issue_tokens_for_user(user, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout(body: TokenRefreshRequest, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    try:
        decoded = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = decoded.get("jti")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token invalido")

    crud_token.revoke_refresh_token_by_jti(db, jti)
    return {"msg": "logout OK"}

#pruebas
#@router.get("/me", response_model=UserOut)
#def read_users_me(current_user: UserOut = Depends(get_current_active_user)):
#    return current_user

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user