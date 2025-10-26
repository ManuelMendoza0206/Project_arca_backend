from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Union
#correo
from pydantic import validator, EmailStr

class Settings(BaseSettings):
    #heredando de basesettings indicamos que no sea un basenormal y que lea automaticamente las varibles de entorno
    #del .en
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MEDIA_DIR: str = "./media"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    DEFAULT_ADMIN_EMAIL: str
    DEFAULT_ADMIN_PASSWORD: str
    #
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    #
    #correo
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str  
    MAIL_FROM: EmailStr
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = "ZooConnect"

    FRONTEND_RESET_PASSWORD_URL: AnyHttpUrl = "http://localhost:3000/reset-password" 
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    #

    @field_validator("CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
