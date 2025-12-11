from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
from datetime import date, datetime

from app.models.tarea import (
    TipoTarea, TareaRecurrente, Tarea,
    RegistroAlimentacion, DetalleAlimentacion
)
from app.models.animal import Animal, Habitat
from app.models.user import User
from app.core.enums import UserRole

from app.schemas.tarea import (
    TipoTareaCreate, TipoTareaUpdate,
    TareaRecurrenteCreate, TareaRecurrenteUpdate, 
    TareaCreate,
    TareaAlimentacionCompletar, DetalleAlimentacionCreate, TareaTratamientoCompletar
)
from app.schemas.transacciones import DetalleSalidaCreate

from app.crud.transacciones import _procesar_salida_transaccional

#TIPO TAREA
def get_tipo_tarea(db: Session, id: int) -> Optional[TipoTarea]:
    return db.query(TipoTarea).filter(TipoTarea.id_tipo_tarea == id).first()

def get_tipo_tarea_by_nombre(db: Session, nombre: str) -> Optional[TipoTarea]:
    return db.query(TipoTarea).filter(TipoTarea.nombre_tipo_tarea == nombre).first()

def get_tipos_tarea_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(TipoTarea)
    if not include_inactive:
        query = query.filter(TipoTarea.is_active == True)
    return query.order_by(TipoTarea.nombre_tipo_tarea)

def create_tipo_tarea(db: Session, tipo_tarea_in: TipoTareaCreate) -> TipoTarea:
    db_tipo_tarea = TipoTarea(**tipo_tarea_in.model_dump())
    db.add(db_tipo_tarea)
    try:
        db.commit()
        db.refresh(db_tipo_tarea)
        return db_tipo_tarea
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El tipo de tarea con nombre '{tipo_tarea_in.nombre_tipo_tarea}' ya existe"
        )

def update_tipo_tarea(db: Session, db_tipo_tarea: TipoTarea, tipo_tarea_in: TipoTareaUpdate) -> TipoTarea:
    update_data = tipo_tarea_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tipo_tarea, field, value)
    db.add(db_tipo_tarea)
    try:
        db.commit()
        db.refresh(db_tipo_tarea)
        return db_tipo_tarea
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe otro tipo de tarea con ese nombre")

def delete_tipo_tarea(db: Session, db_tipo_tarea: TipoTarea) -> TipoTarea:
    db_tipo_tarea.is_active = False
    db.add(db_tipo_tarea)
    db.commit()
    db.refresh(db_tipo_tarea)
    return db_tipo_tarea


#TAREA RECURRENTE

def _validate_tarea_fks(db: Session, tipo_tarea_id: int, animal_id: Optional[int], habitat_id: Optional[int]):
    tipo_tarea = get_tipo_tarea(db, tipo_tarea_id)
    if not tipo_tarea or not tipo_tarea.is_active:
        raise HTTPException(status_code=400, detail=f"El Tipo de Tarea ID {tipo_tarea_id} no existe o esta inactivo")

    if animal_id:
        animal = db.query(Animal).filter(Animal.id_animal == animal_id, Animal.is_active == True).first()
        if not animal:
            raise HTTPException(status_code=404, detail=f"Animal ID {animal_id} no encontrado")
    
    if habitat_id:
        habitat = db.query(Habitat).filter(Habitat.id_habitat == habitat_id).first()
        if not habitat:
            raise HTTPException(status_code=404, detail=f"Habitat ID {habitat_id} no encontrado")

def create_tarea_recurrente(db: Session, tarea_in: TareaRecurrenteCreate) -> TareaRecurrente:
    _validate_tarea_fks(db, tarea_in.tipo_tarea_id, tarea_in.animal_id, tarea_in.habitat_id)
    
    db_tarea_recurrente = TareaRecurrente(**tarea_in.model_dump())
    db.add(db_tarea_recurrente)
    try:
        db.commit()
        db.refresh(db_tarea_recurrente)
        db.refresh(db_tarea_recurrente, attribute_names=['tipo_tarea'])
        return db_tarea_recurrente
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Error de integridad: {e.orig}")

def get_tarea_recurrente(db: Session, id: int) -> Optional[TareaRecurrente]:
    return db.query(TareaRecurrente).options(joinedload(TareaRecurrente.tipo_tarea)).filter(TareaRecurrente.id_tarea_recurrente == id).first()

def get_tareas_recurrentes_query(db: Session, include_inactive: bool = False) -> Query:
    query = db.query(TareaRecurrente).options(joinedload(TareaRecurrente.tipo_tarea))
    if not include_inactive:
        query = query.filter(TareaRecurrente.is_active == True)
    return query.order_by(TareaRecurrente.titulo_plantilla)

def update_tarea_recurrente(db: Session, db_tarea_recurrente: TareaRecurrente, tarea_in: TareaRecurrenteUpdate) -> TareaRecurrente:
    update_data = tarea_in.model_dump(exclude_unset=True)
    
    if "tipo_tarea_id" in update_data or "animal_id" in update_data or "habitat_id" in update_data:
        _validate_tarea_fks(
            db, 
            update_data.get("tipo_tarea_id", db_tarea_recurrente.tipo_tarea_id),
            update_data.get("animal_id", db_tarea_recurrente.animal_id),
            update_data.get("habitat_id", db_tarea_recurrente.habitat_id)
        )

    for field, value in update_data.items():
        setattr(db_tarea_recurrente, field, value)

    db.add(db_tarea_recurrente)
    try:
        db.commit()
        db.refresh(db_tarea_recurrente)
        db.refresh(db_tarea_recurrente, attribute_names=['tipo_tarea'])
        return db_tarea_recurrente
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Error de integridad: {e.orig}")

def delete_tarea_recurrente(db: Session, db_tarea_recurrente: TareaRecurrente) -> TareaRecurrente:
    db_tarea_recurrente.is_active = False 
    db.add(db_tarea_recurrente)
    db.commit()
    return db_tarea_recurrente


#TAREAS

def create_tarea_manual(db: Session, tarea_in: TareaCreate) -> Tarea:
    _validate_tarea_fks(db, tarea_in.tipo_tarea_id, tarea_in.animal_id, tarea_in.habitat_id)
    if tarea_in.usuario_asignado_id:
        user = db.query(User).filter(User.id == tarea_in.usuario_asignado_id).first()
        if not user:
             raise HTTPException(status_code=404, detail="Usuario asignado no encontrado")

    db_tarea = Tarea(**tarea_in.model_dump())
    db.add(db_tarea)
    try:
        db.commit()
        db.refresh(db_tarea)
        return db_tarea
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando tarea: {e}")

def get_tareas_query(
    db: Session,
    is_completed: Optional[bool] = None,
    usuario_asignado_id: Optional[int] = None,
    sin_asignar: Optional[bool] = None,
    fecha_programada: Optional[date] = None
) -> Query:
    query = db.query(Tarea).options(
        joinedload(Tarea.tipo_tarea),
        joinedload(Tarea.usuario_asignado),
        joinedload(Tarea.animal),
        joinedload(Tarea.habitat)
    )

    if is_completed is not None:
        query = query.filter(Tarea.is_completed == is_completed)
    if usuario_asignado_id is not None:
        query = query.filter(Tarea.usuario_asignado_id == usuario_asignado_id)
    if sin_asignar is True:
        query = query.filter(Tarea.usuario_asignado_id == None)
    if fecha_programada is not None:
        query = query.filter(Tarea.fecha_programada == fecha_programada)

    return query.order_by(
        Tarea.fecha_programada.asc(), 
        Tarea.is_completed.asc(),
        Tarea.titulo.asc()
    )

def get_tarea(db: Session, id_tarea: int) -> Optional[Tarea]:
    return db.query(Tarea).options(
        joinedload(Tarea.tipo_tarea),
        joinedload(Tarea.usuario_asignado),
        joinedload(Tarea.animal),
        joinedload(Tarea.habitat)
    ).filter(Tarea.id_tarea == id_tarea).first()

def asignar_tarea(db: Session, db_tarea: Tarea, db_usuario_asignar: User) -> Tarea:
    if db_tarea.usuario_asignado_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta tarea ya ha sido asignada")
    
    if db_usuario_asignar.role.name != UserRole.CUIDADOR.value and not db_usuario_asignar.is_admin:
       raise HTTPException(status_code=400, detail=f"El usuario debe ser Cuidador")

    db_tarea.usuario_asignado_id = db_usuario_asignar.id
    db.add(db_tarea)
    try:
        db.commit()
        db.refresh(db_tarea)
        db.refresh(db_tarea, attribute_names=['usuario_asignado', 'tipo_tarea', 'animal', 'habitat'])
        return db_tarea
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al asignar la tarea: {e}")

#COMPLETAR TAREAS

def completar_tarea_simple(db: Session, db_tarea: Tarea, db_usuario: User, notas: Optional[str]) -> Tarea:
    if db_tarea.is_completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La tarea ya ha sido completada")

    if not db_usuario.is_admin and db_tarea.usuario_asignado_id != db_usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para completar esta tarea")

    if db_tarea.tipo_tarea_id == 1: # ID 1 = Alimentación
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta es una tarea de alimentacion. Use el endpoint especifico")
        
    db_tarea.is_completed = True
    db_tarea.fecha_completada = datetime.now()
    db_tarea.notas_completacion = notas
    
    db.add(db_tarea)
    try:
        db.commit()
        db.refresh(db_tarea)
        return db_tarea
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar: {e}")

def completar_tarea_alimentacion(
    db: Session,
    db_tarea: Tarea,
    db_usuario: User,
    payload: TareaAlimentacionCompletar
) -> RegistroAlimentacion:
    
    #validaciones de Estado
    if db_tarea.is_completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La tarea ya ha sido completada")

    if not db_usuario.is_admin and db_tarea.usuario_asignado_id != db_usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para completar esta tarea")

    if db_tarea.tipo_tarea_id != 1: # Hardcoded ID 1 para Alimentacion
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta no es una tarea de alimentacion")

    if not payload.detalles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe proporcionar al menos un detalle de producto")

    #determinar destino
    target_animal_id = db_tarea.animal_id
    target_habitat_id = db_tarea.habitat_id

    if not target_animal_id and not target_habitat_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La tarea de alimentacion no tiene destino (animal/habitat)")

    try:
        #preparar salida inventario
        detalles_salida = []
        for d in payload.detalles:
            if d.cantidad_entregada > 0:
                detalles_salida.append(
                    DetalleSalidaCreate(
                        producto_id=d.producto_id,
                        cantidad_salida=d.cantidad_entregada,
                        animal_id=target_animal_id, 
                        habitat_id=target_habitat_id 
                    )
                )
        
        if not detalles_salida:
             raise ValueError("No se entrego ningun producto (cantidad_entregada > 0)")

        #logica transaccional
        _ = _procesar_salida_transaccional(
            db=db,
            tipo_salida_id=1, # ID 1 = "Consumo Alimentacion"
            detalles=detalles_salida,
            usuario_id=db_usuario.id
        )
        
        #crear registro alimentacion
        db_registro = RegistroAlimentacion(
            usuario_id=db_usuario.id,
            notas_observaciones=payload.notas_observaciones,
            animal_id=target_animal_id,
            habitat_id=target_habitat_id,
            tarea_id=db_tarea.id_tarea
        )
        db.add(db_registro)
        
        detalles_log_objects = [
            DetalleAlimentacion(
                registro_alimentacion=db_registro,
                producto_id=d.producto_id,
                cantidad_entregada=d.cantidad_entregada,
                cantidad_consumida=d.cantidad_consumida
            ) for d in payload.detalles
        ]
        db.add_all(detalles_log_objects)

        #actuliazar tarea
        db_tarea.is_completed = True
        db_tarea.fecha_completada = datetime.now()
        db_tarea.notas_completacion = payload.notas_observaciones
        db_tarea.registro_alimentacion_generado = db_registro
        db.add(db_tarea)

        #commit final
        db.commit()
        
        db.refresh(db_registro)
        db.refresh(db_registro, attribute_names=['usuario', 'animal', 'habitat', 'detalles_alimentacion'])
        return db_registro

    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al procesar la alimentacion: {e}")
    except Exception as e:
        db.rollback()
        print(f"Error critico completando tarea: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor")
    
def completar_tarea_tratamiento(
    db: Session,
    db_tarea: Tarea,
    db_usuario: User,
    payload: TareaTratamientoCompletar
) -> Tarea:
    
    if db_tarea.is_completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La tarea ya ha sido completada")

    if not db_usuario.is_admin and db_tarea.usuario_asignado_id != db_usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para completar esta tarea")

    if db_tarea.tipo_tarea_id != 2: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta no es una tarea de tratamiento medico")

    if not payload.detalles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe indicar que producto uso")

    target_animal_id = db_tarea.animal_id
    target_habitat_id = db_tarea.habitat_id

    if not target_animal_id and not target_habitat_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La tarea no tiene un destino valido")

    try:
        detalles_salida = []
        for d in payload.detalles:
            if d.cantidad_consumida > 0:
                detalles_salida.append(
                    DetalleSalidaCreate(
                        producto_id=d.producto_id,
                        cantidad_salida=d.cantidad_consumida,
                        animal_id=target_animal_id,
                        habitat_id=target_habitat_id
                    )
                )

        if not detalles_salida:
             raise ValueError("La cantidad consumida debe ser mayor a 0")

        _ = _procesar_salida_transaccional(
            db=db,
            tipo_salida_id=2, 
            detalles=detalles_salida,
            usuario_id=db_usuario.id
        )

        db_tarea.is_completed = True
        db_tarea.fecha_completada = datetime.now()
        db_tarea.notas_completacion = payload.notas_observaciones
        

        db.add(db_tarea)
        db.commit()
        db.refresh(db_tarea)
        
        return db_tarea

    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error validando datos: {e}")
    except Exception as e:
        db.rollback()
        print(f"Error crítico completando tratamiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")