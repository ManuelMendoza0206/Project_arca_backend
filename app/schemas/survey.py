from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime

class OpcionEncuestaBase(BaseModel):
    texto_opcion: str
    orden: Optional[int] = None

class OpcionEncuestaCreate(OpcionEncuestaBase):
    pass

class OpcionEncuestaUpdate(BaseModel):
    texto_opcion: Optional[str] = None
    orden: Optional[int] = None

class OpcionEncuestaOut(OpcionEncuestaBase):
    id_opcion: int

    class Config:
        from_attributes = True


class PreguntaEncuestaBase(BaseModel):
    texto_pregunta: str
    es_opcion_unica: bool 
    orden: Optional[int] = None

class PreguntaEncuestaCreate(PreguntaEncuestaBase):
    opciones: Optional[List[OpcionEncuestaCreate]] = None

class PreguntaEncuestaUpdate(BaseModel):
    texto_pregunta: Optional[str] = None
    es_opcion_unica: Optional[bool] = None
    orden: Optional[int] = None

class PreguntaEncuestaOut(PreguntaEncuestaBase):
    id_pregunta: int
    opciones: List[OpcionEncuestaOut] = []

    class Config:
        from_attributes = True

class EncuestaBase(BaseModel):
    titulo: str
    descripcion: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    is_active: bool = True

class EncuestaCreate(EncuestaBase):
    preguntas: Optional[List[PreguntaEncuestaCreate]] = None

class EncuestaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    is_active: Optional[bool] = None

class EncuestaOut(EncuestaBase):
    id_encuesta: int
    preguntas: List[PreguntaEncuestaOut] = []

    class Config:
        from_attributes = True



class RespuestaBase(BaseModel):
    pregunta_id: int
    opcion_id: Optional[int] = None
    respuesta_texto: Optional[str] = None

class RespuestaCreate(RespuestaBase):
    participacion_id: int

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_response_field(cls, data: dict) -> dict:
        opcion_presente = data.get("opcion_id") is not None
        texto_presente = data.get("respuesta_texto") is not None and data.get("respuesta_texto") != ""

        if opcion_presente and texto_presente:
            raise ValueError("No se puede proporcionar 'opcion_id' y 'respuesta_texto' al mismo tiempo")
        if not opcion_presente and not texto_presente:
            raise ValueError("Se debe proporcionar un valor para 'opcion_id' o para 'respuesta_texto'")
        
        return data

class RespuestaUpdate(BaseModel):
    opcion_id: Optional[int] = None
    respuesta_texto: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_response_field_on_update(cls, data: dict) -> dict:
        if 'opcion_id' in data and 'respuesta_texto' in data:
             if data.get("opcion_id") is not None and data.get("respuesta_texto") is not None:
                raise ValueError("No se puede proporcionar 'opcion_id' y 'respuesta_texto' al mismo tiempo")

        return data

class RespuestaOut(RespuestaBase):
    id_respuesta: int
    participacion_id: int

    class Config:
        from_attributes = True


class ParticipacionBase(BaseModel):
    encuesta_id: int

class ParticipacionCreate(ParticipacionBase):
    pass

class ParticipacionUpdate(BaseModel):
    completada: Optional[bool] = None

class ParticipacionOut(ParticipacionBase):
    id_participacion: int
    usuario_id: int
    fecha_participacion: datetime
    completada: bool
    respuestas: List[RespuestaOut] = []

    class Config:
        from_attributes = True