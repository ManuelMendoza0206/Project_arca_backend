from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Query, status
from datetime import date
from decimal import Decimal

from app.models.inventario import (
    Producto, StockLote, EntradaInventario, DetalleEntrada, 
    TipoSalida, Salida, DetalleSalida
)
from app.models.user import User
from app.models.animal import Animal, Habitat

from app.schemas.transacciones import (
    EntradaInventarioCreate, DetalleEntradaCreate, 
    SalidaInventarioCreate, DetalleSalidaCreate,
    TipoSalidaCreate, TipoSalidaUpdate
)
from app.crud.inventario import get_proveedor

#helpers
def _get_or_create_stock_lote(
    db: Session, 
    producto_id: int, 
    lote: str, 
    fecha_caducidad: date
) -> StockLote:

    db_stock_lote = db.query(StockLote).filter(
        StockLote.producto_id == producto_id,
        StockLote.lote == lote,
        StockLote.fecha_caducidad == fecha_caducidad
    ).with_for_update().first()
    
    if not db_stock_lote:
        db_stock_lote = StockLote(
            producto_id=producto_id,
            lote=lote,
            fecha_caducidad=fecha_caducidad,
            cantidad_disponible=Decimal("0.0")
        )
    
    return db_stock_lote

#tiposalida
def get_tipo_salida(db: Session, id: int) -> Optional[TipoSalida]:
    return db.query(TipoSalida).filter(TipoSalida.id_tipo_salida == id).first()

def get_tipos_salida_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(TipoSalida)
    if not include_inactive:
        query = query.filter(TipoSalida.is_active == True)
    return query.order_by(TipoSalida.nombre_tipo_salida)

def create_tipo_salida(db: Session, tipo_in: TipoSalidaCreate) -> TipoSalida:
    db_tipo = TipoSalida(**tipo_in.model_dump())
    db.add(db_tipo)
    try:
        db.commit()
        db.refresh(db_tipo)
        return db_tipo
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El tipo de salida ya existe")

def update_tipo_salida(db: Session, db_tipo: TipoSalida, tipo_in: TipoSalidaUpdate) -> TipoSalida:
    update_data = tipo_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tipo, field, value)
    db.add(db_tipo)
    try:
        db.commit()
        db.refresh(db_tipo)
        return db_tipo
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Error de integridad al actualizar")

def delete_tipo_salida(db: Session, db_tipo: TipoSalida) -> TipoSalida:
    db_tipo.is_active = False
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

#proceso de entrada

def create_entrada_inventario(db: Session, entrada_in: EntradaInventarioCreate, usuario_id: int) -> EntradaInventario:
    #validar proveedor
    db_proveedor = get_proveedor(db, entrada_in.proveedor_id)
    if not db_proveedor or not db_proveedor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El Proveedor ID {entrada_in.proveedor_id} no existe o esta inactivo"
        )

    try:
        #crear header
        db_entrada = EntradaInventario(
            usuario_id=usuario_id,
            proveedor_id=entrada_in.proveedor_id
        )
        db.add(db_entrada)
        lotes_a_actualizar = []
        productos_a_actualizar = []

        #procesar las lineas
        for detalle_in in entrada_in.detalles:
            if detalle_in.cantidad_entrada <= 0:
                raise ValueError("La cantidad de entrada debe ser positiva")
            
            #obtener y bloquear el producto
            db_producto = db.query(Producto).filter(
                Producto.id_producto == detalle_in.producto_id
            ).with_for_update().first()
            
            if not db_producto or not db_producto.is_active:
                raise ValueError(
                    f"El Producto ID {detalle_in.producto_id} no existe o esta inactivo"
                )

            #Obtener o crear y bloquear el stockote
            db_stock_lote = _get_or_create_stock_lote(
                db,
                producto_id=detalle_in.producto_id,
                lote=detalle_in.lote,
                fecha_caducidad=detalle_in.fecha_caducidad
            )
            
            #Crear detalleentrada
            db_detalle = DetalleEntrada(
                entrada=db_entrada,
                producto=db_producto,
                cantidad_entrada=detalle_in.cantidad_entrada,
                fecha_caducidad=detalle_in.fecha_caducidad,
                lote=detalle_in.lote
            )
            db.add(db_detalle)

            #actualizar stocks
            db_stock_lote.cantidad_disponible += detalle_in.cantidad_entrada
            db_producto.stock_actual += detalle_in.cantidad_entrada
            
            lotes_a_actualizar.append(db_stock_lote)
            productos_a_actualizar.append(db_producto)
        
        db.add_all(lotes_a_actualizar)
        db.add_all(productos_a_actualizar)
        
        # Confirmar transacciom
        db.commit() 
        db.refresh(db_entrada)
        db.refresh(db_entrada, attribute_names=['detalles', 'usuario', 'proveedor'])
        
        return db_entrada

    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error procesando entrada: {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"Error critico en entrada: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")
    
#proceso de salida
def get_salida_inventario(db: Session, id: int) -> Optional[Salida]:
    return db.query(Salida).options(
        joinedload(Salida.tipo_salida),
        joinedload(Salida.usuario),
        joinedload(Salida.detalles).options(
            joinedload(DetalleSalida.animal),
            joinedload(DetalleSalida.habitat),
            joinedload(DetalleSalida.producto).options(
                joinedload(Producto.tipo_producto),
                joinedload(Producto.unidad_medida)
            )
        )
    ).filter(Salida.id_salida == id).first()


def _procesar_salida_transaccional(
    db: Session,
    tipo_salida_id: int,
    detalles: List[DetalleSalidaCreate],
    usuario_id: int,
) -> Salida:

    #tipo salida existe
    db_tipo_salida = get_tipo_salida(db, tipo_salida_id)
    if not db_tipo_salida or not db_tipo_salida.is_active:
         raise ValueError(f"El Tipo de Salida ID {tipo_salida_id} no existe o ests inactivo")

    #crear header
    db_salida = Salida(
        usuario_id=usuario_id,
        tipo_salida_id=tipo_salida_id,
    )
    
    productos_a_actualizar = {} 
    
    #procesar detalles
    for detalle_in in detalles:
        cantidad_a_descontar = detalle_in.cantidad_salida
        if cantidad_a_descontar <= 0:
            raise ValueError("La cantidad de salida debe ser positiva")

        db_producto = db.query(Producto).filter(
            Producto.id_producto == detalle_in.producto_id
        ).with_for_update().first()

        if not db_producto or not db_producto.is_active:
            raise ValueError(f"El Producto ID {detalle_in.producto_id} no existe o esta inactivo")
        
        if db_producto.stock_actual < cantidad_a_descontar:
            raise ValueError(f"Stock insuficiente para '{db_producto.nombre_producto}'. Disponible: {db_producto.stock_actual}, Requerido: {cantidad_a_descontar}")
        #logica de destino
        db_animal = None
        db_habitat = None

        if detalle_in.animal_id:
            db_animal = db.query(Animal).filter(Animal.id_animal == detalle_in.animal_id, Animal.is_active == True).first()
            if not db_animal:
                raise ValueError(f"El Animal ID {detalle_in.animal_id} no existe o está inactivo")
        
        elif detalle_in.habitat_id:
            db_habitat = db.query(Habitat).filter(Habitat.id_habitat == detalle_in.habitat_id, Habitat.is_active == True).first()
            if not db_habitat:
                raise ValueError(f"El Habitat ID {detalle_in.habitat_id} no existe")
        
        #FEFO
        cantidad_restante_por_descontar = cantidad_a_descontar
        lotes_disponibles = db.query(StockLote).filter(
            StockLote.producto_id == detalle_in.producto_id,
            StockLote.cantidad_disponible > 0
        ).order_by(StockLote.fecha_caducidad.asc()).with_for_update().all()

        total_stock_en_lotes = sum(lote.cantidad_disponible for lote in lotes_disponibles)

        if total_stock_en_lotes < cantidad_a_descontar:
             raise ValueError(f"Stock inconsistente en lotes para '{db_producto.nombre_producto}'.")

        for lote in lotes_disponibles:
            if cantidad_restante_por_descontar <= 0:
                break
            
            cantidad_a_tomar_del_lote = min(lote.cantidad_disponible, cantidad_restante_por_descontar)
            
            lote.cantidad_disponible -= cantidad_a_tomar_del_lote
            cantidad_restante_por_descontar -= cantidad_a_tomar_del_lote
            db.add(lote)

        #crear setallesalida
        db_detalle = DetalleSalida(
            salida=db_salida,
            producto=db_producto,
            animal=db_animal, 
            habitat=db_habitat,
            cantidad_salida=detalle_in.cantidad_salida
        )
        db.add(db_detalle)
        
        #Actualizar stock
        if db_producto.id_producto not in productos_a_actualizar:
            productos_a_actualizar[db_producto.id_producto] = db_producto
        productos_a_actualizar[db_producto.id_producto].stock_actual -= detalle_in.cantidad_salida

    db.add(db_salida)
    db.add_all(productos_a_actualizar.values())
    
    return db_salida

    
def create_salida_inventario(
    db: Session, 
    salida_in: SalidaInventarioCreate, 
    usuario_id: int
) -> Salida:
    try:
        db_salida = _procesar_salida_transaccional(
            db=db,
            tipo_salida_id=salida_in.tipo_salida,
            detalles=salida_in.detalles,
            usuario_id=usuario_id
        )
        db.commit()
        
        return get_salida_inventario(db, db_salida.id_salida)

    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    except Exception as e:
        db.rollback()
        print(f"Error interno: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

#consultas de estado

def get_entradas_inventario_query(db: Session) -> Query:
    return db.query(EntradaInventario).options(
        joinedload(EntradaInventario.usuario),
        joinedload(EntradaInventario.proveedor),
        
        joinedload(EntradaInventario.detalles).options(
            joinedload(DetalleEntrada.producto).options(
                joinedload(Producto.tipo_producto),
                joinedload(Producto.unidad_medida)
            )
        )
    ).order_by(EntradaInventario.fecha_entrada.desc())

def get_salidas_inventario_query(db: Session) -> Query:
    return db.query(Salida).options(
        joinedload(Salida.usuario),
        joinedload(Salida.tipo_salida),
        
        joinedload(Salida.detalles).options(
            joinedload(DetalleSalida.animal),
            joinedload(DetalleSalida.habitat),
            joinedload(DetalleSalida.producto).options(
                joinedload(Producto.tipo_producto),
                joinedload(Producto.unidad_medida)
            )
        )
    ).order_by(Salida.fecha_salida.desc())

