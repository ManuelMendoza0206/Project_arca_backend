from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.trivia import TriviaCreate, TriviaOut, ParticipacionTriviaCreate, ParticipacionTriviaOut
from app.crud import trivia as crud_trivia
from app.core.dependencies import get_current_active_user, require_admin_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=TriviaOut, dependencies=[Depends(require_admin_user)])
def create_trivia(trivia_in: TriviaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return crud_trivia.create_trivia(db, trivia_in, usuario_id=current_user.id)

@router.get("/", response_model=List[TriviaOut])
def list_trivias(db: Session = Depends(get_db)):
    return crud_trivia.list_trivias(db)

@router.get("/{trivia_id}", response_model=TriviaOut)
def get_trivia(trivia_id: int, db: Session = Depends(get_db)):
    trivia = crud_trivia.get_trivia(db, trivia_id)
    if not trivia:
        raise HTTPException(status_code=404, detail="Trivia no encontrada")
    return trivia


@router.post("/participar", response_model=ParticipacionTriviaOut)
def participar_trivia(
    participacion_in: ParticipacionTriviaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud_trivia.create_participacion_trivia(db, participacion_in, usuario_id=current_user.id)

@router.get("/{trivia_id}/participaciones", response_model=List[ParticipacionTriviaOut], dependencies=[Depends(require_admin_user)])
def list_participaciones_trivia(trivia_id: int, db: Session = Depends(get_db)):
    return crud_trivia.list_participaciones_trivia(db, trivia_id)
