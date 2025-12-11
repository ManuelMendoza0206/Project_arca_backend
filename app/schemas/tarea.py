from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from app.schemas.user import UserOut
from app.schemas.animal import AnimalOut, HabitatOut
from decimal import Decimal

class TipoTareaBase(BaseModel):
    nombre_tipo_tarea: str
    descripcion_tipo_tarea: Optional[str] = None

class TipoTareaCreate(TipoTareaBase):
    pass

class TipoTareaUpdate(BaseModel):
    nombre_tipo_tarea: Optional[str] = None
    descripcion_tipo_tarea: Optional[str] = None
    is_active: Optional[bool] = None

class TipoTareaOut(TipoTareaBase):
    model_config = ConfigDict(from_attributes=True)

    id_tipo_tarea: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


#tareasrecurrentes
class TareaRecurrenteBase(BaseModel):
    titulo_plantilla: str
    descripcion_plantilla: Optional[str] = None
    tipo_tarea_id: int
    frecuencia_cron: str
    animal_id: Optional[int] = None
    habitat_id: Optional[int] = None
    is_active: bool = True

class TareaRecurrenteCreate(TareaRecurrenteBase):
    pass

class TareaRecurrenteUpdate(BaseModel):
    titulo_plantilla: Optional[str] = None
    descripcion_plantilla: Optional[str] = None
    tipo_tarea_id: Optional[int] = None
    frecuencia_cron: Optional[str] = None
    animal_id: Optional[int] = None
    habitat_id: Optional[int] = None
    is_active: Optional[bool] = None

class TareaRecurrenteOut(TareaRecurrenteBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_tarea_recurrente: int
    created_at: datetime
    updated_at: datetime
    
    tipo_tarea: TipoTareaOut

#tareas
class TareaBase(BaseModel):
    titulo: str
    descripcion_tarea: Optional[str] = None
    fecha_programada: date

class TareaOut(TareaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_tarea: int
    is_completed: bool
    fecha_completada: Optional[datetime] = None
    
    tipo_tarea: TipoTareaOut
    usuario_asignado: Optional[UserOut] = None
    animal: Optional[AnimalOut] = None
    habitat: Optional[HabitatOut] = None
    tarea_recurrente_id: Optional[int] = None

class TareaCreate(TareaBase):
    tipo_tarea_id: int
    usuario_asignado_id: Optional[int] = None
    animal_id: Optional[int] = None
    habitat_id: Optional[int] = None

class TareaOut(TareaBase):
    model_config = ConfigDict(from_attributes=True)
    id_tarea: int
    is_completed: bool
    fecha_completada: Optional[datetime] = None
    notas_completacion: Optional[str] = None
    
    tipo_tarea: TipoTareaOut
    usuario_asignado: Optional[UserOut] = None
    animal: Optional[AnimalOut] = None
    habitat: Optional[HabitatOut] = None
    tarea_recurrente_id: Optional[int] = None

class TareaAssign(BaseModel):
    usuario_asignado_id: int

class TareaSimpleCompletar(BaseModel):
    notas_completacion: Optional[str] = None

#alimentacion
class DetalleAlimentacionCreate(BaseModel):
    producto_id: int
    cantidad_entregada: Decimal 

    cantidad_consumida: Optional[Decimal] = None

class TareaAlimentacionCompletar(BaseModel):
    notas_observaciones: Optional[str] = None
    detalles: List[DetalleAlimentacionCreate]


class DetalleAlimentacionOut(DetalleAlimentacionCreate):
    model_config = ConfigDict(from_attributes=True)
    id_detalle_alimentacion: int
    
class RegistroAlimentacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_registro_alimentacion: int
    fecha_alimentacion: datetime
    notas_observaciones: Optional[str] = None
    usuario: UserOut
    animal: Optional[AnimalOut] = None
    habitat: Optional[HabitatOut] = None
    detalles_alimentacion: List[DetalleAlimentacionOut]

#veterinario
class DetalleTratamientoCreate(BaseModel):
    producto_id: int
    cantidad_consumida: Decimal

class TareaTratamientoCompletar(BaseModel):
    notas_observaciones: Optional[str] = None
    detalles: List[DetalleTratamientoCreate]