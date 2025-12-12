from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.concurrency import run_in_threadpool

from fastapi_pagination import add_pagination
from app.core.config import settings
from app.scripts.create_admin import create_default_admin
from app.scripts.seeds import init_db 
from app.core.scheduler import scheduler, setup_scheduler

from app.api.v1 import (
    auth, animals, admin_users, favorite_animals, surveys, 
    trivia, vendp, inventario_admin, transacciones, 
    alimentacion, tareas, veterinario, dashboards, reportes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando ZooConnect API")

    print("Verificando datos semilla")
    await run_in_threadpool(init_db)

    print("Verificando usuario administrador")
    await run_in_threadpool(create_default_admin)
    
    print("Iniciando Scheduler")
    setup_scheduler()
    
    print("Verificacion exitosa")
    
    yield
    
    print("Apagando Zoocoonect")
    if scheduler.running:
        scheduler.shutdown()
        print("APScheduler detenido")
    print("ZooConnect API detenida")


app = FastAPI(
    title="ZooConnect API",
    lifespan=lifespan,
    description="API para la gestion de un zoologico",
    version="5.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/zooconnect/auth", tags=["auth"])
app.include_router(admin_users.router, prefix="/zooconnect/admin_users", tags=["admin"])
app.include_router(animals.router, prefix="/zooconnect/animals")
app.include_router(surveys.router, prefix="/zooconnect/surveys")
app.include_router(trivia.router, prefix="/zooconnect/trivia", tags=["trivia"])
app.include_router(favorite_animals.router, prefix="/zooconnect/favorite_animals")
app.include_router(vendp.router, prefix="/zooconnect/security", tags=["Seguridad 2fa:)"])
app.include_router(inventario_admin.router, prefix="/zooconnect/inventario", tags=["Poderoso inventario"])
app.include_router(transacciones.router, prefix="/zooconnect/transacciones", tags=["Entradas y salidas de inventario"])
app.include_router(alimentacion.router, prefix="/zooconnect/alimentacion", tags=["Alimentacion"])
app.include_router(tareas.router, prefix="/zooconnect/tareas", tags=["Tareas"]) 
app.include_router(veterinario.router, prefix="/zooconnect/veterinario", tags=["Cruz Roja"]) 
app.include_router(dashboards.router, prefix="/zooconnect/dashboards", tags=["Jesus"]) 
app.include_router(reportes.router, prefix="/zooconnect/reportes", tags=["VI"]) 

add_pagination(app)