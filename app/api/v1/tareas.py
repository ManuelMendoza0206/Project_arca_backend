from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import date
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db.session import get_db
from app.core.dependencies import (
    require_admin_user, 
    get_current_active_user, 
    require_task_management_permission
)
from app.models.user import User

from app.crud import tarea as crud_tarea
from app.crud import user as crud_user
from app.schemas import tarea as schemas_tarea
from app.models import tarea as models_tarea

router = APIRouter()

#HELPERS

def _get_tipo_tarea_or_404(id: int, db: Session = Depends(get_db)) -> models_tarea.TipoTarea:
    db_obj = crud_tarea.get_tipo_tarea(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tipo de tarea no encontrado")
    return db_obj

def _get_tarea_recurrente_or_404(id: int, db: Session = Depends(get_db)) -> models_tarea.TareaRecurrente:
    db_obj = crud_tarea.get_tarea_recurrente(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Plantilla de tarea recurrente no encontrada")
    return db_obj

def _get_tarea_or_404(id_tarea: int, db: Session = Depends(get_db)) -> models_tarea.Tarea:
    db_obj = crud_tarea.get_tarea(db, id_tarea)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return db_obj

def _get_cuidador_or_404(id_usuario: int, db: Session = Depends(get_db)) -> User:
    db_user = crud_user.get_user(db, id_usuario)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario a asignar no encontrado")
    return db_user

def get_today():
    return date.today()

#Gestion tipos tare

@router.post("/tipos", response_model=schemas_tarea.TipoTareaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def create_tipo_tarea(
    tipo_tarea_in: schemas_tarea.TipoTareaCreate,
    db: Session = Depends(get_db),
):
    db_obj_check = crud_tarea.get_tipo_tarea_by_nombre(db, tipo_tarea_in.nombre_tipo_tarea)
    if db_obj_check:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El tipo de tarea ya existe")
    return crud_tarea.create_tipo_tarea(db, tipo_tarea_in)

@router.get("/tipos", response_model=List[schemas_tarea.TipoTareaOut])
def list_tipos_tarea_all(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = crud_tarea.get_tipos_tarea_query(db, include_inactive)
    return query.all()

@router.put("/tipos/{id}", response_model=schemas_tarea.TipoTareaOut, dependencies=[Depends(require_admin_user)])
def update_tipo_tarea(
    id: int,
    tipo_tarea_in: schemas_tarea.TipoTareaUpdate,
    db_obj: models_tarea.TipoTarea = Depends(_get_tipo_tarea_or_404),
    db: Session = Depends(get_db),
):
    return crud_tarea.update_tipo_tarea(db, db_obj, tipo_tarea_in)

@router.delete("/tipos/{id}", response_model=schemas_tarea.TipoTareaOut, dependencies=[Depends(require_admin_user)])
def soft_delete_tipo_tarea(
    db_obj: models_tarea.TipoTarea = Depends(_get_tipo_tarea_or_404),
    db: Session = Depends(get_db),
):
    return crud_tarea.delete_tipo_tarea(db, db_obj)


#Gestion tareas recurrentes

@router.post("/recurrentes", response_model=schemas_tarea.TareaRecurrenteOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def create_tarea_recurrente(
    tarea_in: schemas_tarea.TareaRecurrenteCreate,
    db: Session = Depends(get_db),
):
    return crud_tarea.create_tarea_recurrente(db, tarea_in)

@router.get("/recurrentes", response_model=Page[schemas_tarea.TareaRecurrenteOut], dependencies=[Depends(require_admin_user)])
def list_tareas_recurrentes(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = crud_tarea.get_tareas_recurrentes_query(db, include_inactive)
    return paginate(query)

@router.get("/recurrentes/{id}", response_model=schemas_tarea.TareaRecurrenteOut, dependencies=[Depends(require_admin_user)])
def get_tarea_recurrente(
    db_obj: models_tarea.TareaRecurrente = Depends(_get_tarea_recurrente_or_404),
):
    return db_obj

@router.put("/recurrentes/{id}", response_model=schemas_tarea.TareaRecurrenteOut, dependencies=[Depends(require_admin_user)])
def update_tarea_recurrente(
    id: int,
    tarea_in: schemas_tarea.TareaRecurrenteUpdate,
    db_obj: models_tarea.TareaRecurrente = Depends(_get_tarea_recurrente_or_404),
    db: Session = Depends(get_db),
):
    return crud_tarea.update_tarea_recurrente(db, db_obj, tarea_in)

@router.delete("/recurrentes/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_user)])
def delete_tarea_recurrente(
    db_obj: models_tarea.TareaRecurrente = Depends(_get_tarea_recurrente_or_404),
    db: Session = Depends(get_db),
):
    crud_tarea.delete_tarea_recurrente(db, db_obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#Gestion de tareas

@router.post("/", response_model=schemas_tarea.TareaOut, dependencies=[Depends(require_admin_user)])
def create_tarea_manual(
    tarea_in: schemas_tarea.TareaCreate,
    db: Session = Depends(get_db)
):
    return crud_tarea.create_tarea_manual(db, tarea_in)

@router.get("/mis-tareas", response_model=Page[schemas_tarea.TareaOut])
def list_mis_tareas(
    fecha: Annotated[date, Depends(get_today)],
    is_completed: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = crud_tarea.get_tareas_query(
        db,
        is_completed=is_completed,
        usuario_asignado_id=current_user.id,
        fecha_programada=fecha
    )
    return paginate(query)

@router.get("/sin-asignar", response_model=Page[schemas_tarea.TareaOut], dependencies=[Depends(require_admin_user)])
def list_tareas_sin_asignar(
    db: Session = Depends(get_db),
):
    query = crud_tarea.get_tareas_query(db, is_completed=False, sin_asignar=True)
    return paginate(query)

@router.get("/asignadas-hoy", response_model=Page[schemas_tarea.TareaOut], dependencies=[Depends(require_admin_user)])
def list_tareas_asignadas_hoy(
    fecha: Annotated[date, Depends(get_today)],
    db: Session = Depends(get_db),
):
    query = crud_tarea.get_tareas_query(db, fecha_programada=fecha)
    return paginate(query)

@router.put("/{id_tarea}/asignar", response_model=schemas_tarea.TareaOut, dependencies=[Depends(require_admin_user)])
def assign_tarea(
    body: schemas_tarea.TareaAssign,
    db_tarea: models_tarea.Tarea = Depends(_get_tarea_or_404),
    db: Session = Depends(get_db),
):
    db_usuario = _get_cuidador_or_404(body.usuario_asignado_id, db)
    return crud_tarea.asignar_tarea(db, db_tarea=db_tarea, db_usuario_asignar=db_usuario)


#Ejecuion tareas

@router.post("/{id_tarea}/completar-simple", response_model=schemas_tarea.TareaOut)
def completar_tarea_simple(
    body: schemas_tarea.TareaSimpleCompletar,
    db_tarea: models_tarea.Tarea = Depends(_get_tarea_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db_tarea.usuario_asignado_id is None:
        raise HTTPException(status_code=400, detail="La tarea no ha sido asignada aun")
    
    return crud_tarea.completar_tarea_simple(
        db=db,
        db_tarea=db_tarea,
        db_usuario=current_user,
        notas=body.notas_completacion
    )

@router.post("/{id_tarea}/completar-alimentacion", response_model=schemas_tarea.RegistroAlimentacionOut)
def completar_tarea_alimentacion(
    body: schemas_tarea.TareaAlimentacionCompletar,
    db_tarea: models_tarea.Tarea = Depends(_get_tarea_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db_tarea.usuario_asignado_id is None:
         raise HTTPException(status_code=400, detail="La tarea no ha sido asignada aún")
        
    return crud_tarea.completar_tarea_alimentacion(
        db=db,
        db_tarea=db_tarea,
        db_usuario=current_user,
        payload=body
    )

@router.post("/{id_tarea}/completar-tratamiento", response_model=schemas_tarea.TareaOut)
def complete_task_tratamiento(
    id_tarea: int,
    payload: schemas_tarea.TareaTratamientoCompletar,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    tarea = crud_tarea.get_tarea(db, id_tarea)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    return crud_tarea.completar_tarea_tratamiento(
        db=db, 
        db_tarea=tarea, 
        db_usuario=current_user, 
        payload=payload
    )