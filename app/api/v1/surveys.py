from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_active_user, require_admin_user
from app.crud import survey as crud_survey

from app.schemas.survey import (
    EncuestaCreate, EncuestaUpdate, EncuestaOut,
    PreguntaEncuestaCreate, PreguntaEncuestaUpdate, PreguntaEncuestaOut,
    OpcionEncuestaCreate, OpcionEncuestaUpdate, OpcionEncuestaOut,
    ParticipacionCreate, ParticipacionUpdate, ParticipacionOut,
    RespuestaCreate, RespuestaUpdate, RespuestaOut
)

router = APIRouter()


@router.post("/surveys/", response_model=EncuestaOut, tags=["Encuestas"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def create_encuesta(encuesta_in: EncuestaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return crud_survey.create_encuesta(db, encuesta_in, usuario_id=current_user.id)

@router.get("/surveys/", response_model=List[EncuestaOut], tags=["Encuestas"])
def list_encuestas(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud_survey.list_encuestas(db, skip=skip, limit=limit)

@router.get("/surveys/{encuesta_id}", response_model=EncuestaOut, tags=["Encuestas"])
def get_encuesta(encuesta_id: int, db: Session = Depends(get_db)):
    encuesta = crud_survey.get_encuesta(db, encuesta_id)
    if not encuesta:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    return encuesta

@router.put("/surveys/{encuesta_id}", response_model=EncuestaOut, tags=["Encuestas"], dependencies=[Depends(require_admin_user)])
def update_encuesta(encuesta_id: int, encuesta_in: EncuestaUpdate, db: Session = Depends(get_db)):
    encuesta = crud_survey.update_encuesta(db, encuesta_id, encuesta_in)
    if not encuesta:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    return encuesta

@router.delete("/surveys/{encuesta_id}", tags=["Encuestas"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_user)])
def delete_encuesta(encuesta_id: int, db: Session = Depends(get_db)):
    if not crud_survey.delete_encuesta(db, encuesta_id):
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    return None


@router.post("/surveys/{encuesta_id}/preguntas", response_model=PreguntaEncuestaOut, tags=["Preguntas"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def add_pregunta_a_encuesta(encuesta_id: int, pregunta_in: PreguntaEncuestaCreate, db: Session = Depends(get_db)):
    pregunta = crud_survey.add_pregunta_a_encuesta(db, encuesta_id, pregunta_in)
    if not pregunta:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada para añadir la pregunta")
    return pregunta

@router.put("/surveys/preguntas/{pregunta_id}", response_model=PreguntaEncuestaOut, tags=["Preguntas"], dependencies=[Depends(require_admin_user)])
def update_pregunta(pregunta_id: int, pregunta_in: PreguntaEncuestaUpdate, db: Session = Depends(get_db)):
    pregunta = crud_survey.update_pregunta(db, pregunta_id, pregunta_in)
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return pregunta

@router.delete("/surveys/preguntas/{pregunta_id}", tags=["Preguntas"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_user)])
def delete_pregunta(pregunta_id: int, db: Session = Depends(get_db)):
    if not crud_survey.delete_pregunta(db, pregunta_id):
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return None


@router.post("/surveys/preguntas/{pregunta_id}/opciones", response_model=OpcionEncuestaOut, tags=["Opciones"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def add_opcion_a_pregunta(pregunta_id: int, opcion_in: OpcionEncuestaCreate, db: Session = Depends(get_db)):
    try:
        return crud_survey.add_opcion_a_pregunta(db, pregunta_id, opcion_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/surveys/opciones/{opcion_id}", response_model=OpcionEncuestaOut, tags=["Opciones"], dependencies=[Depends(require_admin_user)])
def update_opcion(opcion_id: int, opcion_in: OpcionEncuestaUpdate, db: Session = Depends(get_db)):
    opcion = crud_survey.update_opcion(db, opcion_id, opcion_in)
    if not opcion:
        raise HTTPException(status_code=404, detail="Opción no encontrada")
    return opcion

@router.delete("/surveys/opciones/{opcion_id}", tags=["Opciones"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_user)])
def delete_opcion(opcion_id: int, db: Session = Depends(get_db)):
    if not crud_survey.delete_opcion(db, opcion_id):
        raise HTTPException(status_code=404, detail="Opción no encontrada")
    return None


@router.post("/participations/", response_model=ParticipacionOut, tags=["Participaciones"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_user)])
def create_participacion(participacion_in: ParticipacionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    try:
        return crud_survey.create_participacion(db, participacion_in, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/participations/{participacion_id}", response_model=ParticipacionOut, tags=["Participaciones"], dependencies=[Depends(get_current_active_user)])
def get_participacion(participacion_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    participacion = crud_survey.get_participacion(db, participacion_id)
    if not participacion or participacion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Participacion no encontrada o no pertenece al usuario")
    return participacion

@router.put("/participations/{participacion_id}", response_model=ParticipacionOut, tags=["Participaciones"], dependencies=[Depends(get_current_active_user)])
def update_participacion(participacion_id: int, participacion_in: ParticipacionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    participacion = crud_survey.get_participacion(db, participacion_id)
    if not participacion or participacion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Participacion no encontrada o no pertenece al usuario")
    return crud_survey.update_participacion(db, participacion_id, participacion_in)

@router.delete("/participations/{participacion_id}", tags=["Participaciones"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
def delete_participacion(participacion_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    participacion = crud_survey.get_participacion(db, participacion_id)
    if not participacion or participacion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Participacion no encontrada o no pertenece al usuario")
    crud_survey.delete_participacion(db, participacion_id)
    return None

#pruebas
@router.get("/participations/", response_model=List[ParticipacionOut], tags=["Participaciones"])
def list_user_participaciones(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return crud_survey.list_user_participaciones(db, usuario_id=current_user.id)


@router.get("/surveys/{encuesta_id}/stats", tags=["Encuestas"])
def get_survey_stats(encuesta_id: int, db: Session = Depends(get_db)):
    return crud_survey.get_survey_stats(db, encuesta_id)


#@router.get("/participacionslist/", response_model=List[ParticipacionOut], tags=["Participaciones"])
#def list_encuestas(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
#    return crud_survey.list_encuestas(db, skip=skip, limit=limit)

#
@router.post("/responses/", response_model=RespuestaOut, tags=["Respuestas"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_user)])
def create_respuesta(respuesta_in: RespuestaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    try:
        return crud_survey.create_respuesta(db, respuesta_in, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/responses/{respuesta_id}", response_model=RespuestaOut, tags=["Respuestas"], dependencies=[Depends(get_current_active_user)])
def get_respuesta(respuesta_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    respuesta = crud_survey.get_respuesta(db, respuesta_id)
    if not respuesta or respuesta.participacion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada o no pertenece al usuario")
    return respuesta

@router.put("/responses/{respuesta_id}", response_model=RespuestaOut, tags=["Respuestas"], dependencies=[Depends(get_current_active_user)])
def update_respuesta(respuesta_id: int, respuesta_in: RespuestaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    respuesta = crud_survey.get_respuesta(db, respuesta_id)
    if not respuesta or respuesta.participacion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada o no pertenece al usuario")
    return crud_survey.update_respuesta(db, respuesta_id, respuesta_in)

@router.delete("/responses/{respuesta_id}", tags=["Respuestas"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
def delete_respuesta(respuesta_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    respuesta = crud_survey.get_respuesta(db, respuesta_id)
    if not respuesta or respuesta.participacion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada o no pertenece al usuario")
    crud_survey.delete_respuesta(db, respuesta_id)
    return None