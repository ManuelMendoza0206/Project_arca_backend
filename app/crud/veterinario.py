from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime

from app.models import veterinario as models_vet
from app.models.animal import Animal
from app.models.user import User
from app.models.inventario import Producto, UnidadMedida
from app.models.tarea import TareaRecurrente, Tarea
from datetime import date

from app.schemas import veterinario as schemas_vet

#HELPERS

def _get_historial_or_404(db: Session, historial_id: int) -> models_vet.HistorialMedico:
    historial = db.query(models_vet.HistorialMedico).filter(
        models_vet.HistorialMedico.id_historial == historial_id
    ).first()
    if not historial:
        raise HTTPException(status_code=404, detail="Historial medico no encontrado")
    return historial

def _check_historial_editable(historial: models_vet.HistorialMedico):
    """
    Si el historial esta CERRADO (estado=False), no se permite ninguna modificacion ni hijo
    """
    if not historial.estado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este historial medico esta CERRADO. No se pueden agregar items ni editarlo"
        )

#TIPO ATENCION

def get_tipo_atencion(db: Session, id: int) -> Optional[models_vet.TipoAtencion]:
    return db.query(models_vet.TipoAtencion).filter(models_vet.TipoAtencion.id_tipo_atencion == id).first()

def get_tipos_atencion_query(db: Session, include_inactive: bool = False):
    query = db.query(models_vet.TipoAtencion)
    if not include_inactive:
        query = query.filter(models_vet.TipoAtencion.is_active == True)
    return query.order_by(models_vet.TipoAtencion.nombre_tipo_atencion)

def create_tipo_atencion(db: Session, obj_in: schemas_vet.TipoAtencionCreate):
    db_obj = models_vet.TipoAtencion(**obj_in.model_dump())
    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un tipo de atencion con ese nombre")

def update_tipo_atencion(db: Session, id: int, obj_in: schemas_vet.TipoAtencionUpdate):
    db_obj = get_tipo_atencion(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tipo de atencion no encontrado")

    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El nombre ya esta en uso por otro tipo de atencion")

def delete_tipo_atencion(db: Session, id: int):
    db_obj = get_tipo_atencion(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tipo de atencion no encontrado")
    
    db_obj.is_active = False
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


#TIPO EXAMEN

def get_tipo_examen(db: Session, id: int) -> Optional[models_vet.TipoExamen]:
    return db.query(models_vet.TipoExamen).filter(models_vet.TipoExamen.id_tipo_examen == id).first()

def get_tipos_examen_query(db: Session, include_inactive: bool = False):
    query = db.query(models_vet.TipoExamen)
    if not include_inactive:
        query = query.filter(models_vet.TipoExamen.is_active == True)
    return query.order_by(models_vet.TipoExamen.nombre_tipo_examen)

def create_tipo_examen(db: Session, obj_in: schemas_vet.TipoExamenCreate):
    db_obj = models_vet.TipoExamen(**obj_in.model_dump())
    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un tipo de examen con ese nombre")

def update_tipo_examen(db: Session, id: int, obj_in: schemas_vet.TipoExamenUpdate):
    db_obj = get_tipo_examen(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tipo de examen no encontrado")

    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El nombre ya está en uso por otro tipo de examen")

def delete_tipo_examen(db: Session, id: int):
    db_obj = get_tipo_examen(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Tipo de examen no encontrado")
    
    db_obj.is_active = False
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

#HISTORIAL MEDICO

def create_historial(
    db: Session, 
    historial_in: schemas_vet.HistorialMedicoCreate, 
    veterinario_id: int
) -> models_vet.HistorialMedico:
    
    animal = db.query(Animal).filter(Animal.id_animal == historial_in.animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")

    tipo = db.query(models_vet.TipoAtencion).filter(
        models_vet.TipoAtencion.id_tipo_atencion == historial_in.tipo_atencion_id
    ).first()
    if not tipo or not tipo.is_active:
        raise HTTPException(status_code=400, detail="Tipo de atencion invalido")

    db_historial = models_vet.HistorialMedico(
        **historial_in.model_dump(),
        veterinario_id=veterinario_id,
        estado=True
    )
    
    db.add(db_historial)
    db.commit()
    db.refresh(db_historial)
    return db_historial

def get_historial(db: Session, historial_id: int) -> Optional[models_vet.HistorialMedico]:
    return db.query(models_vet.HistorialMedico).options(
        joinedload(models_vet.HistorialMedico.animal),
        joinedload(models_vet.HistorialMedico.veterinario),
        joinedload(models_vet.HistorialMedico.tipo_atencion),
        joinedload(models_vet.HistorialMedico.recetas).joinedload(models_vet.RecetaMedica.producto),
        joinedload(models_vet.HistorialMedico.recetas).joinedload(models_vet.RecetaMedica.unidad_medida),
        joinedload(models_vet.HistorialMedico.recetas).joinedload(models_vet.RecetaMedica.usuario_asignado),
        joinedload(models_vet.HistorialMedico.ordenes_examen).joinedload(models_vet.OrdenExamen.tipo_examen),
        joinedload(models_vet.HistorialMedico.procedimientos),
    ).filter(models_vet.HistorialMedico.id_historial == historial_id).first()

def get_historiales_query(
    db: Session, 
    animal_id: Optional[int] = None, 
    estado: Optional[bool] = None,
    veterinario_id: Optional[int] = None
):
    query = db.query(models_vet.HistorialMedico).options(
        joinedload(models_vet.HistorialMedico.animal),
        joinedload(models_vet.HistorialMedico.tipo_atencion),
        joinedload(models_vet.HistorialMedico.veterinario)
    )

    if animal_id:
        query = query.filter(models_vet.HistorialMedico.animal_id == animal_id)
    
    if estado is not None:
        query = query.filter(models_vet.HistorialMedico.estado == estado)

    if veterinario_id:
        query = query.filter(models_vet.HistorialMedico.veterinario_id == veterinario_id)
        
    return query.order_by(models_vet.HistorialMedico.fecha_atencion.desc())

def update_historial(
    db: Session, 
    db_historial: models_vet.HistorialMedico, 
    historial_in: schemas_vet.HistorialMedicoUpdate
) -> models_vet.HistorialMedico:
    
    if not db_historial.estado:
         raise HTTPException(status_code=409, detail="No se puede editar un historial cerrado")

    update_data = historial_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_historial, field, value)

    db.add(db_historial)
    db.commit()
    db.refresh(db_historial)
    return db_historial

#PROCEDIMIENTOS MEDICOS

def create_procedimiento(
    db: Session, 
    procedimiento_in: schemas_vet.ProcedimientoCreate, 
    historial_id: int
):
    historial = _get_historial_or_404(db, historial_id)
    
    _check_historial_editable(historial)

    db_proc = models_vet.ProcedimientoMedico(
        **procedimiento_in.model_dump(),
        historial_medico_id=historial_id,
        estado="Pendiente"
    )
    db.add(db_proc)
    db.commit()
    db.refresh(db_proc)
    return db_proc

def update_procedimiento(
    db: Session,
    procedimiento_id: int,
    proc_in: schemas_vet.ProcedimientoUpdate
):
    db_proc = db.query(models_vet.ProcedimientoMedico).filter(
        models_vet.ProcedimientoMedico.id_procedimiento == procedimiento_id
    ).first()
    
    if not db_proc:
        raise HTTPException(status_code=404, detail="Procedimiento no encontrado")

    if not db_proc.historial.estado:
         raise HTTPException(status_code=409, detail="El historial asociado esta cerrado")

    update_data = proc_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_proc, field, value)

    db.add(db_proc)
    db.commit()
    db.refresh(db_proc)
    return db_proc

def delete_procedimiento(db: Session, procedimiento_id: int):
    db_proc = db.query(models_vet.ProcedimientoMedico).filter(
        models_vet.ProcedimientoMedico.id_procedimiento == procedimiento_id
    ).first()
    
    if not db_proc:
        raise HTTPException(status_code=404, detail="Procedimiento no encontrado")

    if not db_proc.historial.estado:
         raise HTTPException(status_code=409, detail="El historial asociado esta cerrado")

    db.delete(db_proc)
    db.commit()
    return {"detail": "Procedimiento eliminado"}

#RECETAS 
def create_receta(
    db: Session, 
    receta_in: schemas_vet.RecetaMedicaCreate, 
    historial_id: int
) -> models_vet.RecetaMedica:
    
    #1 Validar historial
    historial = _get_historial_or_404(db, historial_id)
    _check_historial_editable(historial)

    #2 Validar inventario
    producto = db.query(Producto).filter(Producto.id_producto == receta_in.producto_id).first()
    if not producto or not producto.is_active:
        raise HTTPException(status_code=400, detail="El producto recetado no existe en inventario")

    if receta_in.unidad_medida_id:
        unidad = db.query(UnidadMedida).filter(UnidadMedida.id_unidad == receta_in.unidad_medida_id).first()
        if not unidad or not unidad.is_active:
             raise HTTPException(status_code=400, detail="La unidad de medida no es valida")

    #3 Validar usuario
    if receta_in.usuario_asignado_id:
        usuario = db.query(User).filter(User.id == receta_in.usuario_asignado_id).first()
        if not usuario:
             raise HTTPException(status_code=404, detail="El usuario asignado para la tarea no existe")
        

    #4 Crear objeto receta
    db_receta = models_vet.RecetaMedica(
        **receta_in.model_dump(),
        historial_medico_id=historial_id
    )
    db.add(db_receta)
    db.flush() 

    #logica hibrida
    if receta_in.generar_tarea_automatica:
        
        titulo_tarea = f"Tratamiento: {receta_in.producto_id} (Ver Receta) - {historial.animal.nombre_animal}"
        
        # CASO A tarea recurrente y cron
        if receta_in.frecuencia_cron:
            nueva_plantilla = TareaRecurrente(
                titulo_plantilla=titulo_tarea,
                descripcion_plantilla=f"Seguir instrucciones receta ID {db_receta.id_receta}",
                tipo_tarea_id=2,
                usuario_asignado_id=receta_in.usuario_asignado_id,
                frecuencia_cron=receta_in.frecuencia_cron,
                is_active=True,
                animal_id=historial.animal_id,
                habitat_id=historial.animal.habitat_id
            )
            db.add(nueva_plantilla)
        
        # CASO B tarea simple sin cron
        else:
            nueva_tarea = Tarea(
                titulo=f"Dosis Única: {titulo_tarea}",
                descripcion_tarea=receta_in.instrucciones_administracion or "Aplicar dosis unica",
                tipo_tarea_id=2,
                
                fecha_programada=date.today(),
                
                usuario_asignado_id=receta_in.usuario_asignado_id,
                animal_id=historial.animal_id,
                habitat_id=historial.animal.habitat_id,
                is_completed=False,
                
                tarea_recurrente_id=None 
            )
            db.add(nueva_tarea)

    try:
        db.commit()
        db.refresh(db_receta)
        return db_receta
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar la receta")

def delete_receta(db: Session, receta_id: int):
    db_receta = db.query(models_vet.RecetaMedica).filter(
        models_vet.RecetaMedica.id_receta == receta_id
    ).first()
    
    if not db_receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    if not db_receta.historial.estado:
         raise HTTPException(status_code=409, detail="El historial esta cerrado")

    db.delete(db_receta)
    db.commit()
    return {"detail": "Receta eliminada"}

#EXAMEN

def create_orden_examen(
    db: Session, 
    orden_in: schemas_vet.OrdenExamenCreate, 
    historial_id: int
):
    historial = _get_historial_or_404(db, historial_id)
    _check_historial_editable(historial)

    tipo = db.query(models_vet.TipoExamen).filter(
        models_vet.TipoExamen.id_tipo_examen == orden_in.tipo_examen_id
    ).first()
    if not tipo or not tipo.is_active:
        raise HTTPException(status_code=400, detail="Tipo de examen invalido")
    #crear orden
    db_orden = models_vet.OrdenExamen(
        **orden_in.model_dump(),
        historial_medico_id=historial_id,
        estado="Solicitado"
    )
    db.add(db_orden)
    db.commit()
    db.refresh(db_orden)
    return db_orden

def delete_orden_examen(db: Session, orden_id: int):
    db_orden = db.query(models_vet.OrdenExamen).filter(models_vet.OrdenExamen.id_orden == orden_id).first()
    if not db_orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    if not db_orden.historial.estado:
         raise HTTPException(status_code=409, detail="Historial cerrado")

    if db_orden.resultados:
        raise HTTPException(status_code=409, detail="No se puede eliminar una orden que ya tiene resultados cargados")

    db.delete(db_orden)
    db.commit()
    return {"detail": "Orden de examen eliminada"}


def create_resultado_examen(
    db: Session,
    orden_id: int,
    resultado_in: schemas_vet.ResultadoExamenCreate,
    file_url: str,
    public_id: str
):

    orden = db.query(models_vet.OrdenExamen).filter(models_vet.OrdenExamen.id_orden == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="La orden de examen no existe")

    _check_historial_editable(orden.historial)

    db_resultado = models_vet.ResultadoExamen(
        orden_examen_id=orden_id,
        conclusiones=resultado_in.conclusiones,
        archivo_url=file_url,
        public_id=public_id
    )
    db.add(db_resultado)

    orden.estado = "Completado"
    db.add(orden)

    try:
        db.commit()
        db.refresh(db_resultado)
        return db_resultado
    except Exception as e:
        db.rollback()
        raise e

def delete_resultado_examen(db: Session, resultado_id: int):
    db_resultado = db.query(models_vet.ResultadoExamen).filter(
        models_vet.ResultadoExamen.id_resultado == resultado_id
    ).first()
    
    if not db_resultado:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    if not db_resultado.orden.historial.estado:
         raise HTTPException(status_code=409, detail="Historial cerrado")

    public_id_to_delete = db_resultado.public_id
    orden_asociada = db_resultado.orden

    db.delete(db_resultado)
    
    otros_resultados = [r for r in orden_asociada.resultados if r.id_resultado != resultado_id]
    if not otros_resultados:
        orden_asociada.estado = "Solicitado"
        db.add(orden_asociada)

    db.commit()
    return {"detail": "Resultado eliminado", "public_id": public_id_to_delete}