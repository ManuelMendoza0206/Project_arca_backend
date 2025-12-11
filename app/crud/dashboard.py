from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from datetime import date
from typing import Dict, List, Any

from app.models.animal import Animal, Especie
from app.models.user import User
from app.models.inventario import Producto
from app.models.tarea import Tarea

def get_dashboard_kpis(db: Session) -> Dict[str, int]:
    today = date.today()

    total_animales = db.query(func.count(Animal.id_animal))\
        .filter(Animal.is_active == True).scalar() or 0

    total_usuarios = db.query(func.count(User.id))\
        .filter(User.is_active == True).scalar() or 0

    alertas_stock = db.query(func.count(Producto.id_producto))\
        .filter(
            Producto.is_active == True,
            Producto.stock_actual <= Producto.stock_minimo
        ).scalar() or 0

    tareas_pendientes = db.query(func.count(Tarea.id_tarea))\
        .filter(
            Tarea.fecha_programada <= today,
            Tarea.is_completed == False
        ).scalar() or 0

    return {
        "total_animales": total_animales,
        "total_usuarios": total_usuarios,
        "alertas_stock": alertas_stock,
        "tareas_pendientes": tareas_pendientes
    }

def get_animales_por_grupo(db: Session, agrupar_por: str) -> List[Dict[str, Any]]:
    columnas_validas = {
        "filo": Especie.filo,
        "clase": Especie.clase,
        "orden": Especie.orden,
        "familia": Especie.familia,
        "especie": Especie.nombre_especie 
    }

    columna_grupo = columnas_validas.get(agrupar_por.lower(), Especie.clase)

    resultados = db.query(
        columna_grupo, 
        func.count(Animal.id_animal)
    ).join(Animal.especie)\
     .filter(Animal.is_active == True)\
     .group_by(columna_grupo)\
     .all()

    data = [
        {"label": row[0], "value": row[1]} 
        for row in resultados
    ]
    
    return data


def get_tareas_status_hoy(db: Session) -> Dict[str, Any]:
    today = date.today()

    total_hoy = db.query(func.count(Tarea.id_tarea))\
        .filter(Tarea.fecha_programada == today).scalar() or 0
        
    completadas = db.query(func.count(Tarea.id_tarea))\
        .filter(
            Tarea.fecha_programada == today,
            Tarea.is_completed == True
        ).scalar() or 0

    pendientes = total_hoy - completadas

    return {
        "total_hoy": total_hoy,
        "resumen": [
            {"estado": "Completada", "cantidad": completadas, "color": "#10B981"},
            {"estado": "Pendiente", "cantidad": pendientes, "color": "#F59E0B"}
        ]
    }