from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db.session import get_db
from app.core.dependencies import require_animal_management_permission, require_admin_user
from app.models.user import User

from app.crud import transacciones as crud_transacciones
from app.crud import inventario as crud_inventario
from app.schemas import transacciones as schemas_tra
from app.schemas import inventario as schemas_inv
from app.models import inventario as models_inv

router = APIRouter()

#ENTRADAS

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
        
    return crud_transacciones.create_entrada_inventario(
        db=db, 
        entrada_in=entrada_in, 
        usuario_id=current_user.id
    )

@router.get("/entradas", response_model=Page[schemas_tra.EntradaInventarioOut])
def list_entradas_inventario(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):
    query = crud_transacciones.get_entradas_inventario_query(db)
    return paginate(query)


#SALIDAS

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

    return crud_transacciones.create_salida_inventario(
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
    db_salida = crud_transacciones.get_salida_inventario(db, id)
    if not db_salida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salida de inventario no encontrada"
        )
    return db_salida

@router.get("/salidas", response_model=Page[schemas_tra.SalidaOut])
def list_salidas_inventario(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):
    query = crud_transacciones.get_salidas_inventario_query(db)
    return paginate(query)

#REPORTES

@router.get("/alertas-stock", response_model=Page[schemas_inv.ProductoOut])
def list_productos_con_stock_bajo(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):
    query = crud_inventario.get_productos_con_stock_bajo_query(db)
    return paginate(query)


#TIPOS SALIDAS
def _get_tipo_salida_or_404(
    id: int, db: Session = Depends(get_db)
) -> models_inv.TipoSalida:
    db_obj = crud_transacciones.get_tipo_salida(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tipo de salida no encontrado")
    return db_obj

@router.post("/tipos-salida", response_model=schemas_tra.TipoSalidaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def create_tipo_salida(
    tipo_in: schemas_tra.TipoSalidaCreate,
    db: Session = Depends(get_db),
):
    return crud_transacciones.create_tipo_salida(db, tipo_in)

@router.get("/tipos-salida", response_model=Page[schemas_tra.TipoSalidaOut], dependencies=[Depends(require_admin_user)])
def list_tipos_salida(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = crud_transacciones.get_tipos_salida_query(db, include_inactive)
    return paginate(query)

@router.put("/tipos-salida/{id}", response_model=schemas_tra.TipoSalidaOut, dependencies=[Depends(require_admin_user)])
def update_tipo_salida(
    id: int,
    tipo_in: schemas_tra.TipoSalidaUpdate,
    db_obj: models_inv.TipoSalida = Depends(_get_tipo_salida_or_404),
    db: Session = Depends(get_db),
):
    return crud_transacciones.update_tipo_salida(db, db_obj, tipo_in)

@router.delete("/tipos-salida/{id}", response_model=schemas_tra.TipoSalidaOut, dependencies=[Depends(require_admin_user)])
def delete_tipo_salida(
    db_obj: models_inv.TipoSalida = Depends(_get_tipo_salida_or_404),
    db: Session = Depends(get_db),
):
    return crud_transacciones.soft_delete_tipo_salida(db, db_obj)