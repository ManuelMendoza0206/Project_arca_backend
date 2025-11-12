from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.session import get_db
from app.core.dependencies import require_animal_management_permission
from app.models.user import User
from app.crud import transacciones
from app.schemas import inventario as schemas_inv
from app.models import inventario as models_inv

from app.schemas import transacciones as schemas_tra
router = APIRouter()

#entradas
@router.post("/entradas", response_model=schemas_tra.EntradaInventarioOut, status_code=status.HTTP_201_CREATED)
def create_entrada_inventario_endpoint(
    entrada_in: schemas_tra.EntradaInventarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):
    if not entrada_in.detalles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La entrada debe tener al menos un detalle"
        )
        
    return transacciones.create_entrada_inventario(
        db=db, 
        entrada_in=entrada_in, 
        usuario_id=current_user.id
    )

@router.post("/salidas", response_model=schemas_tra.SalidaOut, status_code=status.HTTP_201_CREATED)
def create_salida_inventario_endpoint(
    salida_in: schemas_tra.SalidaInventarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):
    if not salida_in.detalles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La salida debe tener al menos un detalle"
        )

    return transacciones.create_salida_inventario(
        db=db, 
        salida_in=salida_in, 
        usuario_id=current_user.id
    )

@router.get("/salidas/{id}", response_model=schemas_tra.SalidaOut)
def get_salida_inventario_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):

    db_salida = transacciones.get_salida_inventario(db, id)
    if not db_salida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salida de inventario no encontrada"
        )
    return db_salida