from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class AdminUserCreate(UserBase):
    password: str
    role_id: int
    is_active: Optional[bool] = True

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserUpdateProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    role_id: int
    photo_url: Optional[str] = None 
    created_at: datetime 

    class Config:
        from_attributes = True
