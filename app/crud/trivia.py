from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.trivia import Trivia, ParticipacionTrivia
from app.schemas.trivia import TriviaCreate, ParticipacionTriviaCreate


def create_trivia(db: Session, trivia_in: TriviaCreate, usuario_id: int) -> Trivia:
    trivia = Trivia(
        fecha_trivia=trivia_in.fecha_trivia,
        cantidad_preguntas=trivia_in.cantidad_preguntas,
        dificultad=trivia_in.dificultad,
        usuario_id=usuario_id
    )
    db.add(trivia)
    db.commit()
    db.refresh(trivia)
    return trivia


def get_trivia(db: Session, trivia_id: int) -> Optional[Trivia]:
    return db.query(Trivia).filter(Trivia.id_trivia == trivia_id).first()


def list_trivias(db: Session) -> List[Trivia]:
    return db.query(Trivia).all()


def create_participacion_trivia(db: Session, participacion_in: ParticipacionTriviaCreate, usuario_id: int) -> ParticipacionTrivia:
    participacion = ParticipacionTrivia(
        usuario_id=usuario_id,
        aciertos=participacion_in.aciertos,
        fecha_trivia=datetime.utcnow(),
        trivia_id=participacion_in.trivia_id
    )
    db.add(participacion)
    db.commit()
    db.refresh(participacion)
    return participacion


def list_participaciones_trivia(db: Session, trivia_id: int) -> List[ParticipacionTrivia]:
    return db.query(ParticipacionTrivia).filter(ParticipacionTrivia.trivia_id == trivia_id).all()
