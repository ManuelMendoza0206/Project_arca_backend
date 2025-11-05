from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AuditLogUser(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class AuditLogOut(BaseModel):
    id: int
    event: str
    timestamp: datetime
    attempted_email: Optional[str] = None

    user: Optional[AuditLogUser] = None 

    class Config:
        from_attributes = True