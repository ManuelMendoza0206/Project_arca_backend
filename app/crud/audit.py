from sqlalchemy.orm import Session
from typing import Optional

from app.models.audit_log import AuditLog
from app.core.enums import AuditEvent

def create_audit_log(
    db: Session,
    *,
    event: AuditEvent,
    user_id: Optional[int] = None,
    attempted_email: Optional[str] = None
) -> None:

    
    email_to_log = attempted_email.lower().strip() if attempted_email else None
    
    db_log = AuditLog(
        event=event.value,
        user_id=user_id,
        attempted_email=email_to_log
    )
    
    db.add(db_log)
    db.commit()