from sqlalchemy.orm import Session, Query, joinedload
from typing import Optional
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.core.enums import AuditEvent

def create_audit_log(
    *,
    event: AuditEvent,
    user_id: Optional[int] = None,
    attempted_email: Optional[str] = None
) -> None:
    db: Session = SessionLocal()
    
    try:
        email_to_log = attempted_email.lower().strip() if attempted_email else None
        
        db_log = AuditLog(
            event=event.value,
            user_id=user_id,
            attempted_email=email_to_log
        )
        
        db.add(db_log)
        db.commit()
    except Exception as e:
        print(f"ERROR EN BACKGROUND TASK (create_audit_log): {e}")
        db.rollback()
    finally:
        db.close()


def get_audit_logs_query(db: Session) -> Query:
    return db.query(AuditLog).options(
        joinedload(AuditLog.user)
    ).order_by(AuditLog.timestamp.desc())