from pydantic import BaseModel, EmailStr, Field, constr, validator
#ret token
import re
#2fa
from typing import Annotated, Union

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
#cambios refresh token jesus
#class TokenRefreshRequest(BaseModel):
#    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    #refresh_token: str
    token_type: str = "bearer"
    #expires_in: int | None = None

    #class Config:
    #    from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayuscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("La contraseña debe contener al menos un numero")
        return v
    
#2fa
class LoginStep2Response(BaseModel):

    step: str = "2fa_required"
    session_token: str 

TOTPCodem = Annotated[str, Field(..., strip_whitespace=True, min_length=6, max_length=6)]
class TOTPLoginRequest(BaseModel):
    session_token: str
    code: TOTPCodem