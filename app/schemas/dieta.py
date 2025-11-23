from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.inventario import ProductoOut, UnidadMedidaOut
 
class DetalleDietaBase(BaseModel):
    producto_id: int
    unidad_medida_id: int
    cantidad: Decimal
    frecuencia: str

class DetalleDietaCreate(DetalleDietaBase):
    pass

class DetalleDietaOut(DetalleDietaBase):
    model_config = ConfigDict(from_attributes=True)
    id_detalle_dieta: int

    producto: ProductoOut
    unidad_medida: UnidadMedidaOut


class DietaBase(BaseModel):
    nombre_dieta: str
    animal_id: Optional[int] = None
    especie_id: Optional[int] = None

class DietaCreate(DietaBase):
    detalles: List[DetalleDietaCreate]

class DietaUpdate(BaseModel):
    nombre_dieta: Optional[str] = None
    animal_id: Optional[int] = None
    especie_id: Optional[int] = None
    detalles: Optional[List[DetalleDietaCreate]] = None

class DietaOut(DietaBase):
    model_config = ConfigDict(from_attributes=True)
    id_dieta: int
    created_at: datetime
    updated_at: datetime
    detalles_dieta: List[DetalleDietaOut]