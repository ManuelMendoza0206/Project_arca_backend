from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from typing import List, Union

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MEDIA_DIR: str = "./media"
    CORS_ORIGINS: List[AnyHttpUrl] | List[str] = ["http://localhost:3000"]
    
    #
    CLOUDINARY_CLOUD_NAME: str="djne2ckoy"
    CLOUDINARY_API_KEY: str="376362916615896"
    CLOUDINARY_API_SECRET: str="31MZumJ8CRWjsck3XjGa4a6LxaI"
    #

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
