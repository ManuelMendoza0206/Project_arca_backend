from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db.session import get_db
from app.core.dependencies import require_animal_management_permission, get_current_active_user

from app.crud import dieta as crud_dieta
from app.crud import tarea as crud_tarea
from app.schemas import dieta as schemas_dieta
from app.models import tarea as models_tarea
from app.models.user import User

router = APIRouter()

#HELPERS

def _get_dieta_or_404(id: int, db: Session = Depends(get_db)) -> models_tarea.Dieta:
    db_obj = crud_dieta.get_dieta(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Dieta no encontrada")
    return db_obj

def _get_tarea_local_or_404(id_tarea: int, db: Session = Depends(get_db)) -> models_tarea.Tarea:
    db_obj = crud_tarea.get_tarea(db, id_tarea)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return db_obj


#DIETAS
@router.post("/dietas", response_model=schemas_dieta.DietaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_animal_management_permission)])
def create_dieta(
    dieta_in: schemas_dieta.DietaCreate,
    db: Session = Depends(get_db),
):
    return crud_dieta.create_dieta(db, dieta_in)

@router.get("/dietas", response_model=Page[schemas_dieta.DietaOut], dependencies=[Depends(require_animal_management_permission)])
def list_dietas(
    db: Session = Depends(get_db),
):
    query = crud_dieta.get_dietas_query(db)
    return paginate(query)

@router.get("/dietas/{id}", response_model=schemas_dieta.DietaOut, dependencies=[Depends(require_animal_management_permission)])
def get_dieta(
    db_obj: models_tarea.Dieta = Depends(_get_dieta_or_404),
):
    return db_obj

@router.put("/dietas/{id}", response_model=schemas_dieta.DietaOut, dependencies=[Depends(require_admin_user := require_animal_management_permission)]) 
def update_dieta(
    id: int,
    dieta_in: schemas_dieta.DietaUpdate,
    db_obj: models_tarea.Dieta = Depends(_get_dieta_or_404),
    db: Session = Depends(get_db),
):
    return crud_dieta.update_dieta(db, db_obj, dieta_in)

@router.delete("/dietas/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_animal_management_permission)])
def soft_delete_dieta(
    db_obj: models_tarea.Dieta = Depends(_get_dieta_or_404),
    db: Session = Depends(get_db),
):
    crud_dieta.delete_dieta(db, db_obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#SUGERENCIAS
@router.get("/{id_tarea}/sugerencia-dieta", response_model=schemas_dieta.DietaOut)
def get_sugerencia_dieta_para_tarea(
    id_tarea: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    db_tarea = _get_tarea_local_or_404(id_tarea, db)

    if db_tarea.tipo_tarea_id != 1 and "alimentacion" not in str(db_tarea.tipo_tarea.nombre_tipo_tarea).lower():
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esta tarea no parece ser de Alimentacion"
        )
      
    if not db_tarea.animal_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La tarea no esta asignada a un animal especifico"
        )

    dieta = crud_dieta.get_dieta_for_animal(db, animal_id=db_tarea.animal_id)
    
    if not dieta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encontro un plan de dieta configurado para este animal o su especie"
        )
        
    return dieta