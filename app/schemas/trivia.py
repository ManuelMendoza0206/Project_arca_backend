from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TriviaBase(BaseModel):
    fecha_trivia: datetime
    cantidad_preguntas: int
    dificultad: str

class TriviaCreate(TriviaBase):
    pass

class TriviaOut(TriviaBase):
    id_trivia: int
    usuario_id: int
    class Config:
        from_attributes = True


class ParticipacionTriviaCreate(BaseModel):
    trivia_id: int
    aciertos: int

class ParticipacionTriviaOut(BaseModel):
    id_participacion_trivia: int
    usuario_id: int
    aciertos: int
    fecha_trivia: datetime
    trivia_id: int
    class Config:
        from_attributes = True
