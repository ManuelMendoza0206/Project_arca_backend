from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app.models.refresh_token import RefreshToken

def create_refresh_token_record(
    db: Session,
    user_id: int,
    jti: str,
    expires_at: datetime,
    device_info: Optional[str] = None
) -> RefreshToken:
    token = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
        device_info=device_info,
        revoked=False,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

def revoke_refresh_token_by_jti(db: Session, jti: str) -> Optional[RefreshToken]:
    token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if not token:
        return None
    if not token.revoked:
        token.revoked = True
        db.add(token)
        db.commit()
        db.refresh(token)
    return token

def is_refresh_token_valid(db: Session, jti: str) -> bool:
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti, RefreshToken.revoked == False)
        .first()
    )
    if not token:
        return False
    return token.expires_at > datetime.now(timezone.utc)
