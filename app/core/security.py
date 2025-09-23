from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import uuid
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str, expires_minutes: int | None = None, extra_claims: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=(expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expires,
        "type": "access"
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: str, expires_days: int | None = None, device_info: str | None = None) -> dict:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=(expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS))
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expires,
        "jti": jti,
        "type": "refresh"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"token": token, "jti": jti, "expires_at": expires, "device_info": device_info}
