from typing import List, Optional
from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.tarea import Dieta, DetalleDieta
from app.models.animal import Animal, Especie
from app.models.inventario import Producto, UnidadMedida

from app.schemas.dieta import DietaCreate, DietaUpdate, DetalleDietaCreate

from app.crud import inventario


def _validate_dieta_fks(
    db: Session, 
    detalles: Optional[List[DetalleDietaCreate]],
    animal_id: Optional[int],
    especie_id: Optional[int]
):
    if not animal_id and not especie_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La dieta debe estar asociada a un animal o a una especie"
        )
    
    if animal_id:
        animal = db.query(Animal).filter(Animal.id_animal == animal_id, Animal.is_active == True).first()
        if not animal:
            raise HTTPException(status_code=404, detail=f"Animal con id {animal_id} no encontrado o inactivo")
    
    if especie_id:
        especie = db.query(Especie).filter(Especie.id_especie == especie_id, Especie.is_active == True).first()
        if not especie:
            raise HTTPException(status_code=404, detail=f"Especie con id {especie_id} no encontrada")

    if detalles is not None:
        if len(detalles) == 0:
            raise HTTPException(status_code=400, detail="La dieta debe tener al menos un detalle (producto)")

        for d in detalles:
            producto = inventario.get_producto(db, d.producto_id)
            if not producto or not producto.is_active:
                raise HTTPException(status_code=400, detail=f"Producto ID {d.producto_id} no encontrado o inactivo")
            
            unidad = inventario.get_unidad_medida(db, d.unidad_medida_id)
            if not unidad or not unidad.is_active:
                raise HTTPException(status_code=400, detail=f"Unidad ID {d.unidad_medida_id} no encontrada o inactiva")

def get_dieta(db: Session, id: int) -> Optional[Dieta]:
    return db.query(Dieta).options(
        joinedload(Dieta.detalles_dieta).options(
            joinedload(DetalleDieta.producto).options(
                joinedload(Producto.tipo_producto),
                joinedload(Producto.unidad_medida)
            ),
            joinedload(DetalleDieta.unidad_medida)
        )
    ).filter(Dieta.id_dieta == id).first()

def create_dieta(db: Session, dieta_in: DietaCreate) -> Dieta:
    _validate_dieta_fks(
        db, 
        detalles=dieta_in.detalles, 
        animal_id=dieta_in.animal_id, 
        especie_id=dieta_in.especie_id
    )
    
    try:
        #header
        dieta_header_data = dieta_in.model_dump(exclude={"detalles"})
        db_dieta = Dieta(**dieta_header_data)
        db.add(db_dieta)
        
        #crear detalles
        detalles_objects = []
        for detalle_in in dieta_in.detalles:
            db_detalle = DetalleDieta(
                **detalle_in.model_dump(),
                dieta=db_dieta
            )
            detalles_objects.append(db_detalle)
        
        db.add_all(detalles_objects)
        
        db.commit()
        db.refresh(db_dieta)
        
        return get_dieta(db, db_dieta.id_dieta) 
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"El animal o especie ya tiene una dieta asignada")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando dieta: {e}")

def get_dieta_for_animal(db: Session, animal_id: int) -> Optional[Dieta]:
    #primero buscamos dieta especficia del animal sino de la especie
    db_dieta = db.query(Dieta).filter(
        Dieta.animal_id == animal_id, 
        Dieta.is_active == True
    ).first()
    
    if db_dieta:
        return get_dieta(db, db_dieta.id_dieta)
    
    #ahora si de la especie
    animal = db.query(Animal).filter(Animal.id_animal == animal_id).first()
    if not animal:
        return None
    
    db_dieta_especie = db.query(Dieta).filter(
        Dieta.especie_id == animal.especie_id,
        Dieta.is_active == True
    ).first()
    
    if db_dieta_especie:
        return get_dieta(db, db_dieta_especie.id_dieta)

    return None

def update_dieta(
    db: Session, 
    db_dieta: Dieta, 
    dieta_in: DietaUpdate
) -> Dieta:
    update_data = dieta_in.model_dump(exclude_unset=True)
    
    if "detalles" in update_data or "animal_id" in update_data or "especie_id" in update_data:
        _validate_dieta_fks(
            db,
            detalles=update_data.get("detalles"),
            animal_id=update_data.get("animal_id", db_dieta.animal_id),
            especie_id=update_data.get("especie_id", db_dieta.especie_id)
        )

    #actualziar header
    detalles_nuevos = update_data.pop("detalles", None)

    for field, value in update_data.items():
        setattr(db_dieta, field, value)
    
    try:
        #Actualizar Detalles
        if detalles_nuevos is not None:
            #reemplzaco ocmpleto
            db.query(DetalleDieta).filter(DetalleDieta.dieta_id == db_dieta.id_dieta).delete()
            
            for detalle_in in detalles_nuevos:
                new_detalle = DetalleDieta(
                    dieta_id=db_dieta.id_dieta,
                    producto_id=detalle_in['producto_id'],
                    unidad_medida_id=detalle_in['unidad_medida_id'],
                    cantidad=detalle_in['cantidad'],
                    frecuencia=detalle_in['frecuencia']
                )
                db.add(new_detalle)

        db.add(db_dieta)
        db.commit()
        db.refresh(db_dieta)
        return get_dieta(db, db_dieta.id_dieta)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de integridad al actualizar dieta")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando dieta: {e}")

def delete_dieta(db: Session, db_dieta: Dieta) -> Dieta:
    db_dieta.is_active = False
    db.add(db_dieta)
    db.commit()
    db.refresh(db_dieta)
    return db_dieta

def get_dietas_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(Dieta).options(
        joinedload(Dieta.detalles_dieta).options(
            joinedload(DetalleDieta.producto).options(
                joinedload(Producto.tipo_producto),
                joinedload(Producto.unidad_medida)
            ),
            joinedload(DetalleDieta.unidad_medida)
        )
    )
    
    if not include_inactive:
        query = query.filter(Dieta.is_active == True)
        
    return query.order_by(Dieta.nombre_dieta)