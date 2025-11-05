from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import date, datetime
from app.core.enums import AnimalState


class MediaBaseAnimal(BaseModel):
    tipo_medio: bool
    url_animal: str = Field(..., max_length=2048)
    titulo_media_animal: str = Field(..., max_length=150)
    descripcion_media_animal: Optional[str] = None

class MediaCreateAnimal(MediaBaseAnimal):
    pass

class MediaOutAnimal(MediaBaseAnimal):
    id_media_animal: int
    public_id: Optional[str] = None
    class Config:
        from_attributes = True

class MediaBaseHabitat(BaseModel):
    tipo_medio: bool
    url_habitat: str = Field(..., max_length=2048)
    titulo_media_habitat: str = Field(..., max_length=150)
    descripcion_media_habitat: Optional[str] = None

class MediaCreateHabitat(MediaBaseHabitat):
    pass

class MediaOutHabitat(MediaBaseHabitat):
    id_media_habitat: int
    public_id: Optional[str] = None
    class Config:
        from_attributes = True


class EspecieBase(BaseModel):
    nombre_cientifico: str = Field(..., max_length=100)
    nombre_especie: str = Field(..., max_length=100)
    filo: str = Field(..., max_length=100)
    clase: str = Field(..., max_length=100)
    orden: str = Field(..., max_length=100)
    familia: str = Field(..., max_length=100)
    descripcion_especie: str

class EspecieCreate(EspecieBase):
    pass

class EspecieUpdate(BaseModel):
    nombre_cientifico: Optional[str] = Field(None, max_length=100)
    nombre_especie: Optional[str] = Field(None, max_length=100)
    filo: Optional[str] = Field(None, max_length=100)
    clase: Optional[str] = Field(None, max_length=100)
    orden: Optional[str] = Field(None, max_length=100)
    familia: Optional[str] = Field(None, max_length=100)
    descripcion_especie: Optional[str] = None
    is_active: bool

class EspecieOut(EspecieBase):
    id_especie: int
    is_active: bool

    class Config:
        from_attributes = True


class HabitatBase(BaseModel):
    nombre_habitat: str = Field(..., max_length=50)
    tipo_habitat: str = Field(..., max_length=80)
    descripcion_habitat: str
    condiciones_climaticas: str = Field(..., max_length=200)

class HabitatCreate(HabitatBase):
    pass

class HabitatUpdate(BaseModel):
    nombre_habitat: Optional[str] = Field(None, max_length=50)
    tipo_habitat: Optional[str] = Field(None, max_length=80)
    descripcion_habitat: Optional[str] = None
    condiciones_climaticas: Optional[str] = Field(None, max_length=200)
    is_active: bool

class HabitatOut(HabitatBase):
    id_habitat: int
    is_active: bool

    class Config:
        from_attributes = True


class AnimalBase(BaseModel):
    nombre_animal: str = Field(..., max_length=100)
    genero: bool
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    procedencia_animal: str = Field(..., max_length=300)
    estado_operativo: AnimalState
    es_publico: bool = True
    descripcion: str

class AnimalCreate(AnimalBase):
    especie_id: int
    habitat_id: int
    #prueba
    @model_validator(mode='after')
    def check_dates(self) -> 'AnimalCreate':
        if self.fecha_nacimiento and self.fecha_ingreso:
            if self.fecha_ingreso < self.fecha_nacimiento:
                raise ValueError("La fecha de ingreso no puede ser anterior a la fecha de nacimiento")
        return self

class AnimalUpdate(BaseModel):
    nombre_animal: Optional[str] = Field(None, max_length=100)
    genero: Optional[bool] = None
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    procedencia_animal: Optional[str] = Field(None, max_length=300)
    estado_operativo: Optional[AnimalState] = None
    es_publico: Optional[bool] = None
    descripcion: Optional[str] = None
    especie_id: Optional[int] = None
    habitat_id: Optional[int] = None

class AnimalOut(AnimalBase):
    id_animal: int
    especie: EspecieOut
    habitat: HabitatOut
    media: List[MediaOutAnimal] = []
    age: Optional[int]
    #is_active : bool
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