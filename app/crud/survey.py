from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional


from app.models.survey import Encuesta, PreguntaEncuesta, OpcionEncuesta, ParticipacionEncuesta, RespuestaUsuario

from app.schemas.survey import (
    EncuestaCreate, EncuestaUpdate,
    PreguntaEncuestaCreate, PreguntaEncuestaUpdate,
    OpcionEncuestaCreate, OpcionEncuestaUpdate,
    ParticipacionCreate, ParticipacionUpdate,
    RespuestaCreate, RespuestaUpdate
)


def create_encuesta(db: Session, encuesta_in: EncuestaCreate, usuario_id: int) -> Encuesta:
    encuesta = Encuesta(
        titulo=encuesta_in.titulo,
        descripcion=encuesta_in.descripcion,
        fecha_inicio=encuesta_in.fecha_inicio,
        fecha_fin=encuesta_in.fecha_fin,
        usuario_creador_id=usuario_id,
        is_active=encuesta_in.is_active
    )
    db.add(encuesta)
    db.flush()

    if encuesta_in.preguntas:
        for pregunta_in in encuesta_in.preguntas:
            pregunta = PreguntaEncuesta(
                encuesta_id=encuesta.id_encuesta,
                texto_pregunta=pregunta_in.texto_pregunta,
                es_opcion_unica=pregunta_in.es_opcion_unica, 
                orden=pregunta_in.orden
            )
            db.add(pregunta)
            db.flush()

            if pregunta.es_opcion_unica and pregunta_in.opciones:
                for opcion_in in pregunta_in.opciones:
                    opcion = OpcionEncuesta(
                        pregunta_id=pregunta.id_pregunta,
                        texto_opcion=opcion_in.texto_opcion,
                        orden=opcion_in.orden
                    )
                    db.add(opcion)
    db.commit()
    db.refresh(encuesta)
    return encuesta

def get_encuesta(db: Session, encuesta_id: int) -> Optional[Encuesta]:
    return db.query(Encuesta).filter(Encuesta.id_encuesta == encuesta_id).first()

def list_encuestas(db: Session, skip: int = 0, limit: int = 100) -> List[Encuesta]:
    return db.query(Encuesta).offset(skip).limit(limit).all()

def update_encuesta(db: Session, encuesta_id: int, encuesta_in: EncuestaUpdate) -> Optional[Encuesta]:
    encuesta = get_encuesta(db, encuesta_id)
    if not encuesta:
        return None
    update_data = encuesta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(encuesta, field, value)
    db.commit()
    db.refresh(encuesta)
    return encuesta

def delete_encuesta(db: Session, encuesta_id: int) -> bool:
    encuesta = get_encuesta(db, encuesta_id)
    if not encuesta:
        return False

    db.delete(encuesta)
    db.commit()
    return True


def get_pregunta(db: Session, pregunta_id: int) -> Optional[PreguntaEncuesta]:
    return db.query(PreguntaEncuesta).filter(PreguntaEncuesta.id_pregunta == pregunta_id).first()

def add_pregunta_a_encuesta(db: Session, encuesta_id: int, pregunta_in: PreguntaEncuestaCreate) -> Optional[PreguntaEncuesta]:
    encuesta = get_encuesta(db, encuesta_id)
    if not encuesta:
        return None
    pregunta = PreguntaEncuesta(
        **pregunta_in.model_dump(exclude_unset=True, exclude={'opciones'}), 
        encuesta_id=encuesta_id
    )
    db.add(pregunta)
    db.commit()
    db.refresh(pregunta)
    return pregunta

def update_pregunta(db: Session, pregunta_id: int, pregunta_in: PreguntaEncuestaUpdate) -> Optional[PreguntaEncuesta]:
    pregunta = get_pregunta(db, pregunta_id)
    if not pregunta:
        return None
    update_data = pregunta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pregunta, field, value)
    db.commit()
    db.refresh(pregunta)
    return pregunta

def delete_pregunta(db: Session, pregunta_id: int) -> bool:
    pregunta = get_pregunta(db, pregunta_id)
    if not pregunta:
        return False
    db.delete(pregunta)
    db.commit()
    return True


def get_opcion(db: Session, opcion_id: int) -> Optional[OpcionEncuesta]:
    return db.query(OpcionEncuesta).filter(OpcionEncuesta.id_opcion == opcion_id).first()

def add_opcion_a_pregunta(db: Session, pregunta_id: int, opcion_in: OpcionEncuestaCreate) -> OpcionEncuesta:
    pregunta = get_pregunta(db, pregunta_id)
    if not pregunta:
        raise ValueError("La pregunta especificada no existe")
    
    if not pregunta.es_opcion_unica:
        raise ValueError("No se pueden añadir opciones a una pregunta de texto abierto")
        
    opcion = OpcionEncuesta(**opcion_in.model_dump(), pregunta_id=pregunta_id)
    db.add(opcion)
    db.commit()
    db.refresh(opcion)
    return opcion

def update_opcion(db: Session, opcion_id: int, opcion_in: OpcionEncuestaUpdate) -> Optional[OpcionEncuesta]:
    opcion = get_opcion(db, opcion_id)
    if not opcion:
        return None
    update_data = opcion_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opcion, field, value)
    db.commit()
    db.refresh(opcion)
    return opcion

def delete_opcion(db: Session, opcion_id: int) -> bool:
    opcion = get_opcion(db, opcion_id)
    if not opcion:
        return False
    db.delete(opcion)
    db.commit()
    return True

def create_participacion(db: Session, participacion_in: ParticipacionEncuesta, usuario_id: int) -> ParticipacionEncuesta:
    existente = db.query(ParticipacionEncuesta).filter_by(
        encuesta_id=participacion_in.encuesta_id, 
        usuario_id=usuario_id
    ).first()
    if existente:
        raise ValueError("El usuario ya ha iniciado una participacion en esta encuesta")
        
    participacion = ParticipacionEncuesta(
        encuesta_id=participacion_in.encuesta_id,
        usuario_id=usuario_id,
        fecha_participacion=datetime.utcnow(),
        completada=False 
    )
    db.add(participacion)
    db.commit()
    db.refresh(participacion)
    return participacion

def get_participacion(db: Session, participacion_id: int) -> Optional[ParticipacionEncuesta]:
    return db.query(ParticipacionEncuesta).filter(ParticipacionEncuesta.id_participacion == participacion_id).first()

def update_participacion(db: Session, participacion_id: int, participacion_in: ParticipacionUpdate) -> Optional[ParticipacionEncuesta]:
    participacion = get_participacion(db, participacion_id)
    if not participacion:
        return None
    update_data = participacion_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(participacion, field, value)
    db.commit()
    db.refresh(participacion)
    return participacion

def delete_participacion(db: Session, participacion_id: int) -> bool:
    participacion = get_participacion(db, participacion_id)
    if not participacion:
        return False
    db.delete(participacion)
    db.commit()
    return True

#prueba
def list_user_participaciones(db: Session, usuario_id: int, skip: int = 0, limit: int = 100) -> List[ParticipacionEncuesta]:
    return (
        db.query(ParticipacionEncuesta)
        .filter(ParticipacionEncuesta.usuario_id == usuario_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
from typing import Optional

def get_survey_stats(db: Session, encuesta_id: int):
    encuesta = db.query(Encuesta).filter(Encuesta.id_encuesta == encuesta_id).first()
    if not encuesta:
        return None

    total_participaciones_completadas = db.query(ParticipacionEncuesta).filter(
        ParticipacionEncuesta.encuesta_id == encuesta_id,
        ParticipacionEncuesta.completada == True
    ).count()

    if total_participaciones_completadas == 0:
        return {
            "total_participaciones": 0,
            "estadisticas_preguntas": {}
        }
    
    stats_query = db.query(
        PreguntaEncuesta.id_pregunta.label('pregunta_id'),
        PreguntaEncuesta.texto_pregunta.label('pregunta_texto'),
        OpcionEncuesta.id_opcion.label('opcion_id'),
        OpcionEncuesta.texto_opcion.label('opcion_texto'),
        func.count(RespuestaUsuario.id_respuesta).label('conteo_respuestas')
    ).outerjoin(
        OpcionEncuesta, PreguntaEncuesta.id_pregunta == OpcionEncuesta.pregunta_id
    ).outerjoin(
        RespuestaUsuario, 
        RespuestaUsuario.opcion_id == OpcionEncuesta.id_opcion
    ).outerjoin(
        ParticipacionEncuesta, 
        (RespuestaUsuario.participacion_id == ParticipacionEncuesta.id_participacion) & (ParticipacionEncuesta.completada == True)
    ).filter(
        PreguntaEncuesta.encuesta_id == encuesta_id
    ).group_by(
        PreguntaEncuesta.id_pregunta,
        PreguntaEncuesta.texto_pregunta,
        OpcionEncuesta.id_opcion,
        OpcionEncuesta.texto_opcion
    ).all()

    estadisticas_preguntas = defaultdict(lambda: {
        'texto_pregunta': '',
        'opciones': {}
    })
    
    for row in stats_query:
        pregunta_id = str(row.pregunta_id)
        opcion_id = str(row.opcion_id)
        
        estadisticas_preguntas[pregunta_id]['texto_pregunta'] = row.pregunta_texto
        estadisticas_preguntas[pregunta_id]['opciones'][opcion_id] = {
            'texto_opcion': row.opcion_texto,
            'conteo_respuestas': row.conteo_respuestas or 0
        }
    
    return {
        "total_participaciones": total_participaciones_completadas,
        "estadisticas_preguntas": dict(estadisticas_preguntas)
    }

def create_respuesta(db: Session, respuesta_in: RespuestaCreate, usuario_id: int) -> RespuestaUsuario:
    participacion = get_participacion(db, respuesta_in.participacion_id)
    if not participacion or participacion.usuario_id != usuario_id:
        raise ValueError("Participacion no valida o no pertenece al usuario")

    pregunta = get_pregunta(db, respuesta_in.pregunta_id)
    if not pregunta or pregunta.encuesta_id != participacion.encuesta_id:
        raise ValueError("La pregunta no pertenece a la encuesta de esta participacion")

    if respuesta_in.opcion_id:
        if not pregunta.es_opcion_unica:
            raise ValueError("No se puede dar una opcion como respuesta a una pregunta de texto")
        opcion = get_opcion(db, respuesta_in.opcion_id)
        if not opcion or opcion.pregunta_id != pregunta.id_pregunta:
            raise ValueError("La opcion proporcionada no es valida para esta pregunta")
    elif respuesta_in.respuesta_texto:
        if pregunta.es_opcion_unica:
            raise ValueError("No se puede dar una respuesta de texto a una pregunta de opcion multiple")
    
    respuesta = RespuestaUsuario(**respuesta_in.model_dump())
    db.add(respuesta)
    db.commit()
    db.refresh(respuesta)
    return respuesta

def get_respuesta(db: Session, respuesta_id: int) -> Optional[RespuestaUsuario]:
    return db.query(RespuestaUsuario).filter(RespuestaUsuario.id_respuesta == respuesta_id).first()

def update_respuesta(db: Session, respuesta_id: int, respuesta_in: RespuestaUpdate) -> Optional[RespuestaUsuario]:
    respuesta = get_respuesta(db, respuesta_id)
    if not respuesta:
        return None
    update_data = respuesta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(respuesta, field, value)
    db.commit()
    db.refresh(respuesta)
    return respuesta

def delete_respuesta(db: Session, respuesta_id: int) -> bool:
    respuesta = get_respuesta(db, respuesta_id)
    if not respuesta:
        return False
    db.delete(respuesta)
    db.commit()
    return True