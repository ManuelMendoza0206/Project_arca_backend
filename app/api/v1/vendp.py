from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.core.security import verify_password
from app.core.encryption import decrypt_data
from app.crud import two_factor as crud_2fa
from app.schemas.two_factor import (
    TOTPSetupResponse, TOTPVerifyRequest, 
    TOTPBackupCodesResponse, TOTPDisableRequest
)

router = APIRouter()

@router.post("/2fa/enable", response_model=TOTPSetupResponse, summary="Iniciar activacion de 2FA")
def setup_2fa(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Paso 1: Genera un secreto y una URI para el QR --> Uusuario escanea
    """
    if current_user.is_totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA esta activo:)")
    
    #secreto
    secret = crud_2fa.generate_totp_secret()
    crud_2fa.save_totp_secret_for_user(db, user=current_user, secret=secret)
    
    #uri
    otpauth_uri = crud_2fa.get_otpauth_uri(secret, current_user.email)
    
    return {"secret": secret, "otpauth_uri": otpauth_uri}

@router.post("/2fa/verify", response_model=TOTPBackupCodesResponse, summary="Verificar y activar 2FA :)")
def verify_2fa(
    body: TOTPVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Paso 2: El usuario envia el codigo de la app
    """
    if current_user.is_totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA esta activo:)")
    if not current_user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes iniciar el proceso /2fa/enable primero")

    try:
        secret = decrypt_data(current_user.totp_secret)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al descifrar el secreto")
    
    if not crud_2fa.verify_totp_code(secret, body.totp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Codigo invalido. TRY AGAIN")

    crud_2fa.activate_totp_for_user(db, user=current_user)
    
    plaintext_codes = crud_2fa.generate_and_store_backup_codes(db, user=current_user)
    
    return {"backup_codes": plaintext_codes}

@router.post("/2fa/disable", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar 2FA")
def disable_2fa(
    body: TOTPDisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    if not current_user.is_totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA YA NO ESTA ACTIVO:(")
    
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contraseña incorrecta")
        
    crud_2fa.disable_totp_for_user(db, user=current_user)
    
    return None