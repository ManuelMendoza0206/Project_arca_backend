from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.scripts.create_admin import create_default_admin
from app.core.config import settings
from app.core.filesystem import ensure_upload_dirs_exist
from app.api.v1 import auth, animals, admin_users, favorite_animals, surveys, trivia, vendp, inventario_admin, transacciones
from fastapi.concurrency import run_in_threadpool
#pagination
from fastapi_pagination import add_pagination
# app
app = FastAPI(
    title="ZooConnect API",
    description="API para la gestion de un zoologico",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/zooconnect/auth", tags=["auth"])
app.include_router(admin_users.router, prefix="/zooconnect/admin_users", tags=["admin"])
app.include_router(animals.router, prefix="/zooconnect/animals")
app.include_router(surveys.router, prefix="/zooconnect/surveys", tags=["surveys"])
app.include_router(trivia.router, prefix="/zooconnect/trivia", tags=["trivia"])
app.include_router(favorite_animals.router, prefix="/zooconnect/favorite_animals")
app.include_router(vendp.router, prefix="/zooconnect/security", tags=["Seguridad 2fa:)"])
app.include_router(inventario_admin.router, prefix="/zooconnect/inventario", tags=["Poderoso inventario"])
app.include_router(transacciones.router, prefix="/zooconnect/transacciones", tags=["Entradas y salidas de inventario"])
add_pagination(app)
@app.on_event("startup")
async def startup_event():
    print("ZooConnect API iniciada")
    print("Verificando usuario administrador por defecto")
    await run_in_threadpool(create_default_admin)
    print("Verificacion completa")

@app.on_event("shutdown")
async def shutdown_event():
    print("ZooConnect API detenida")