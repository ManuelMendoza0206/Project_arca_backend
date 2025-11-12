from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.inventario import  Producto,  StockLote, EntradaInventario, DetalleEntrada
from app.models.user import User 

from app.schemas.transacciones import EntradaInventarioCreate, DetalleEntradaCreate, SalidaInventarioCreate, DetalleSalidaCreate
from app.crud.inventario import get_proveedor
from datetime import date
from decimal import Decimal

from app.models.inventario import Salida, DetalleSalida
from app.models.animal import Animal

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
        db.refresh(db_entrada, attribute_names=['detalles', 'usuario', 'proveedor'])
        
        return db_entrada

    except (ValueError, IntegrityError) as e:
        db.rollback()
        print(f"Error en transaccion de entrada: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la entrada: {e}"
        )
    except Exception as e:
        db.rollback()
        print(f"Error inesperado en transaccion de entrada: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {e}"
        )
    

def get_salida_inventario(db: Session, id: int) -> Optional[Salida]:
    return db.query(Salida).options(
        joinedload(Salida.usuario),
        joinedload(Salida.detalles).options(
            joinedload(DetalleSalida.animal),
            joinedload(DetalleSalida.producto).options(
                joinedload(Producto.tipo_producto),
                joinedload(Producto.unidad_medida)
            )
        )
    ).filter(Salida.id_salida == id).first()


def create_salida_inventario(
    db: Session, 
    salida_in: SalidaInventarioCreate, 
    usuario_id: int
) -> Salida:

    try:
        #Crear el HEADER de la salida
        db_salida = Salida(
            usuario_id=usuario_id,
            tipo_salida=salida_in.tipo_salida
        )
        db.add(db_salida)
        
        productos_a_actualizar = {} #id_producto: db_producto
        
        #procesar detalles
        for detalle_in in salida_in.detalles:
            cantidad_a_descontar = detalle_in.cantidad_salida
            if cantidad_a_descontar <= 0:
                raise ValueError("La cantidad de salida debe ser positiva")

            #3obtener y BLOQUEAR producto
            #with_for_update() para evitar que se realicen dos procesos a la vez
            db_producto = db.query(Producto).filter(
                Producto.id_producto == detalle_in.producto_id
            ).with_for_update().first()

            if not db_producto or not db_producto.is_active:
                raise ValueError(f"El Producto ID {detalle_in.producto_id} no existe o esta inactivo")
            
            #revision stock
            if db_producto.stock_actual < cantidad_a_descontar:
                raise ValueError(f"Stock insuficiente para '{db_producto.nombre_producto}'. Disponible: {db_producto.stock_actual}, Requerido: {cantidad_a_descontar}")

            #validar animal
            db_animal = None
            if detalle_in.animal_id:
                db_animal = db.query(Animal).filter(
                    Animal.id_animal == detalle_in.animal_id,
                    Animal.is_active == True
                ).first()
                if not db_animal:
                    raise ValueError(f"El Animal ID {detalle_in.animal_id} no existe o esta inactivo")

            #logica FEFO 
            cantidad_restante_por_descontar = cantidad_a_descontar
            
            lotes_disponibles = db.query(StockLote).filter(
                StockLote.producto_id == detalle_in.producto_id,
                StockLote.cantidad_disponible > 0
            ).order_by(
                StockLote.fecha_caducidad.asc()
            ).with_for_update().all()

            #validacion consistencia
            total_stock_en_lotes = sum(lote.cantidad_disponible for lote in lotes_disponibles)
            if total_stock_en_lotes < cantidad_a_descontar:
                raise ValueError(f"Stock inconsistente para '{db_producto.nombre_producto}'. Lotes suman: {total_stock_en_lotes}, Requerido: {cantidad_a_descontar}")

            #descontar de los lotes
            for lote in lotes_disponibles:
                if cantidad_restante_por_descontar <= 0:
                    break

                cantidad_a_tomar_del_lote = min(
                    lote.cantidad_disponible, 
                    cantidad_restante_por_descontar
                )
                
                lote.cantidad_disponible -= cantidad_a_tomar_del_lote
                cantidad_restante_por_descontar -= cantidad_a_tomar_del_lote
                
                db.add(lote)

            #crear el detallesalida
            db_detalle = DetalleSalida(
                salida=db_salida,
                producto=db_producto,
                animal=db_animal,
                cantidad_salida=detalle_in.cantidad_salida
            )
            db.add(db_detalle)
            
            #actualziando stock
            if db_producto.id_producto not in productos_a_actualizar:
                productos_a_actualizar[db_producto.id_producto] = db_producto
            
            productos_a_actualizar[db_producto.id_producto].stock_actual -= detalle_in.cantidad_salida

        db.add_all(productos_a_actualizar.values())

        #Confirmar la transaccion
        db.commit()
        return get_salida_inventario(db, db_salida.id_salida)

    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la salida: {e}"
        )
    except Exception as e:
        db.rollback()
        print(f"Error inesperado en transaccion de salida: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {e}"
        )