
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.core.enums import AnimalState


class MediaBase(BaseModel):
    tipo_medio: bool
    url: str = Field(..., max_length=200)
    titulo: str = Field(..., max_length=150)
    descripcion: Optional[str] = None

class MediaCreate(MediaBase):
    pass

class MediaOut(MediaBase):
    id_media: int
    public_id: Optional[str] = None
    class Config:
        from_attributes = True


class EspecieBase(BaseModel):
    nombre_cientifico: str = Field(..., max_length=100)
    nombre: str = Field(..., max_length=100)
    filo: str = Field(..., max_length=100)
    clase: str = Field(..., max_length=100)
    orden: str = Field(..., max_length=100)
    familia: str = Field(..., max_length=100)
    genero: str = Field(..., max_length=100)
    descripcion: str

class EspecieCreate(EspecieBase):
    pass

class EspecieUpdate(BaseModel):
    nombre_cientifico: Optional[str] = Field(None, max_length=100)
    nombre: Optional[str] = Field(None, max_length=100)
    filo: Optional[str] = Field(None, max_length=100)
    clase: Optional[str] = Field(None, max_length=100)
    orden: Optional[str] = Field(None, max_length=100)
    familia: Optional[str] = Field(None, max_length=100)
    genero: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None

class EspecieOut(EspecieBase):
    id_especie: int
    is_active: bool

    class Config:
        from_attributes = True


class HabitatBase(BaseModel):
    nombre_habitat: str = Field(..., max_length=50)
    tipo: str = Field(..., max_length=80)
    descripcion: str
    condiciones_climaticas: str = Field(..., max_length=200)

class HabitatCreate(HabitatBase):
    pass

class HabitatUpdate(BaseModel):
    nombre_habitat: Optional[str] = Field(None, max_length=50)
    tipo: Optional[str] = Field(None, max_length=80)
    descripcion: Optional[str] = None
    condiciones_climaticas: Optional[str] = Field(None, max_length=200)

class HabitatOut(HabitatBase):
    id_habitat: int
    is_active: bool

    class Config:
        from_attributes = True


class AnimalBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    genero: bool
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    procedencia: str = Field(..., max_length=300)
    estado_operativo: AnimalState
    es_publico: bool = True
    descripcion: str

class AnimalCreate(AnimalBase):
    especie_id: int
    habitat_id: int

class AnimalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    genero: Optional[bool] = None
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    procedencia: Optional[str] = Field(None, max_length=300)
    estado_operativo: Optional[AnimalState] = None
    es_publico: Optional[bool] = None
    descripcion: Optional[str] = None
    especie_id: Optional[int] = None
    habitat_id: Optional[int] = None

class AnimalOut(AnimalBase):
    id_animal: int
    especie: EspecieOut
    habitat: HabitatOut
    media: List[MediaOut] = []

    class Config:
        from_attributes = True


class AnimalFavoritoCreate(BaseModel):
    animal_id: int

class AnimalFavoritoOut(BaseModel):
    id_animal_favorito: int
    fecha_guardado: datetime
    animal: AnimalOut 

    class Config:
        from_attributes = True