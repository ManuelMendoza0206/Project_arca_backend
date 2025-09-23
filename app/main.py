from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.scripts.create_admin import create_default_admin

from app.core.config import settings
from app.core.filesystem import ensure_upload_dirs_exist

from app.api.v1 import auth, animals, admin_users, surveys, trivia

app = FastAPI(
    title="ZooConnect API",
    description="API para la gestion de un zoologico",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_upload_dirs_exist()

# Registro de routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_users.router, prefix="/api/v1/admin_users", tags=["admin"])
app.include_router(animals.router, prefix="/api/v1/animals", tags=["animals"])
app.include_router(surveys.router, prefix="/api/v1")
app.include_router(trivia.router, prefix="/api/v1/trivia", tags=["trivia"])
@app.on_event("startup")
async def startup_event():
    print("ZooConnect API iniciada")
    print("Verificando usuario administrador por defecto")
    create_default_admin()
    print("Verificacion completa")


@app.on_event("shutdown")
async def shutdown_event():
    print("ZooConnect API detenida")