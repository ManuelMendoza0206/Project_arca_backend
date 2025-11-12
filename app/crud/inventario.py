from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional

from app.models.inventario import TipoProducto, UnidadMedida, Proveedor, Producto

from app.schemas.inventario import (
    TipoProductoCreate, TipoProductoUpdate,
    UnidadMedidaCreate, UnidadMedidaUpdate,
    ProveedorCreate, ProveedorUpdate,
    ProductoCreate, ProductoUpdate
)
#CRUD tipoproducto
def get_tipo_producto(db: Session, id: int) -> Optional[TipoProducto]:
    return db.query(TipoProducto).filter(TipoProducto.id_tipo_producto == id).first()

def get_tipo_producto_by_nombre(db: Session, nombre: str) -> Optional[TipoProducto]:
    return db.query(TipoProducto).filter(TipoProducto.nombre_tipo_producto == nombre).first()

def get_tipos_producto_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(TipoProducto)
    if not include_inactive:
        query = query.filter(TipoProducto.is_active == True)
    return query.order_by(TipoProducto.nombre_tipo_producto)

def create_tipo_producto(db: Session, tipo_producto_in: TipoProductoCreate) -> TipoProducto:
    db_tipo_producto = TipoProducto(**tipo_producto_in.model_dump())
    
    db.add(db_tipo_producto)
    try:
        db.commit()
        db.refresh(db_tipo_producto)
        return db_tipo_producto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El tipo de producto con ese nombre ya existe"
        )

def update_tipo_producto(
    db: Session, 
    db_tipo_producto: TipoProducto, 
    tipo_producto_in: TipoProductoUpdate
) -> TipoProducto:
    update_data = tipo_producto_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tipo_producto, field, value)
    
    db.add(db_tipo_producto)
    try:
        db.commit()
        db.refresh(db_tipo_producto)
        return db_tipo_producto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe otro tipo de producto con ese nombre"
        )

def delete_tipo_producto(db: Session, db_tipo_producto: TipoProducto) -> TipoProducto:
    db_tipo_producto.is_active = False
    db.add(db_tipo_producto)
    db.commit()
    db.refresh(db_tipo_producto)
    return db_tipo_producto


#CRUD UnidadMedida
def get_unidad_medida(db: Session, id: int) -> Optional[UnidadMedida]:
    return db.query(UnidadMedida).filter(UnidadMedida.id_unidad == id).first()

def get_unidades_medida_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(UnidadMedida)
    if not include_inactive:
        query = query.filter(UnidadMedida.is_active == True)
    return query.order_by(UnidadMedida.nombre_unidad)

def create_unidad_medida(db: Session, unidad_medida_in: UnidadMedidaCreate) -> UnidadMedida:
    db_unidad_medida = UnidadMedida(**unidad_medida_in.model_dump())
    db.add(db_unidad_medida)
    try:
        db.commit()
        db.refresh(db_unidad_medida)
        return db_unidad_medida
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La unidad de medida o abreviatura ya existe"
        )

def update_unidad_medida(
    db: Session, 
    db_unidad_medida: UnidadMedida, 
    unidad_medida_in: UnidadMedidaUpdate
) -> UnidadMedida:
    update_data = unidad_medida_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_unidad_medida, field, value)
    db.add(db_unidad_medida)
    try:
        db.commit()
        db.refresh(db_unidad_medida)
        return db_unidad_medida
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El nombre o abreviatura ya existen"
        )

def delete_unidad_medida(db: Session, db_unidad_medida: UnidadMedida) -> UnidadMedida:
    db_unidad_medida.is_active = False
    db.add(db_unidad_medida)
    db.commit()
    db.refresh(db_unidad_medida)
    return db_unidad_medida

# CRUD Proveedor

def get_proveedor(db: Session, id: int) -> Optional[Proveedor]:
    return db.query(Proveedor).filter(Proveedor.id_proveedor == id).first()

def get_proveedores_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(Proveedor)
    if not include_inactive:
        query = query.filter(Proveedor.is_active == True)
    return query.order_by(Proveedor.nombre_proveedor)

def create_proveedor(db: Session, proveedor_in: ProveedorCreate) -> Proveedor:
    db_proveedor = Proveedor(**proveedor_in.model_dump())
    db.add(db_proveedor)
    try:
        db.commit()
        db.refresh(db_proveedor)
        return db_proveedor
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El proveedor con ese nombre o email ya existe"
        )

def update_proveedor(
    db: Session, 
    db_proveedor: Proveedor, 
    proveedor_in: ProveedorUpdate
) -> Proveedor:
    update_data = proveedor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_proveedor, field, value)
    db.add(db_proveedor)
    try:
        db.commit()
        db.refresh(db_proveedor)
        return db_proveedor
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El nombre o email ya existen."
        )

def delete_proveedor(db: Session, db_proveedor: Proveedor) -> Proveedor:
    db_proveedor.is_active = False
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

# CRUD Producto

def _validate_producto_fks(
    db: Session, 
    tipo_producto_id: int, 
    unidad_medida_id: int
):

    tipo_producto = get_tipo_producto(db, tipo_producto_id)
    if not tipo_producto or not tipo_producto.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El Tipo de Producto ID {tipo_producto_id} no existe o esta inactivo"
        )
    
    unidad_medida = get_unidad_medida(db, unidad_medida_id)
    if not unidad_medida or not unidad_medida.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La Unidad de Medida ID {unidad_medida_id} no existe o esta inactiva"
        )

def get_producto(db: Session, id: int) -> Optional[Producto]:
    return db.query(Producto).options(
        joinedload(Producto.tipo_producto),
        joinedload(Producto.unidad_medida)
    ).filter(Producto.id_producto == id).first()

def get_productos_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(Producto).options(
        joinedload(Producto.tipo_producto),
        joinedload(Producto.unidad_medida)
    )
    if not include_inactive:
        query = query.filter(Producto.is_active == True)
        
    return query.order_by(Producto.nombre_producto)

def create_producto(db: Session, producto_in: ProductoCreate) -> Producto:
    _validate_producto_fks(
        db, 
        producto_in.tipo_producto_id, 
        producto_in.unidad_medida_id
    )
    
    db_producto = Producto(**producto_in.model_dump())
    
    db.add(db_producto)
    try:
        db.commit()
        db.refresh(db_producto)
        db.refresh(db_producto, attribute_names=['tipo_producto', 'unidad_medida'])
        return db_producto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El producto con nombre '{producto_in.nombre_producto}' ya existe"
        )

def update_producto(
    db: Session, 
    db_producto: Producto, 
    producto_in: ProductoUpdate
) -> Producto:
    update_data = producto_in.model_dump(exclude_unset=True)

    if "tipo_producto_id" in update_data or "unidad_medida_id" in update_data:
        _validate_producto_fks(
            db,
            tipo_producto_id=update_data.get("tipo_producto_id", db_producto.tipo_producto_id),
            unidad_medida_id=update_data.get("unidad_medida_id", db_producto.unidad_medida_id)
        )
    
    for field, value in update_data.items():
        setattr(db_producto, field, value)
        
    db.add(db_producto)
    try:
        db.commit()
        db.refresh(db_producto)
        db.refresh(db_producto, attribute_names=['tipo_producto', 'unidad_medida'])
        return db_producto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El nombre del producto ya existe"
        )

def delete_producto(db: Session, db_producto: Producto) -> Producto:

    db_producto.is_active = False
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto