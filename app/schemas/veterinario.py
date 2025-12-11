from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.schemas.user import UserOut 
from app.schemas.animal import AnimalOut
from app.schemas.inventario import ProductoOut, UnidadMedidaOut


class CatalogoBase(BaseModel):
    descripcion: Optional[str] = None
#TIPO ATENCION
class TipoAtencionCreate(CatalogoBase):
    nombre_tipo_atencion: str

class TipoAtencionUpdate(BaseModel):
    nombre_tipo_atencion: Optional[str] = None
    descripcion: Optional[str] = None
    is_active: Optional[bool] = None

class TipoAtencionOut(CatalogoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_tipo_atencion: int
    nombre_tipo_atencion: str
    is_active: bool

#TIPO EXAMEN
class TipoExamenCreate(CatalogoBase):
    nombre_tipo_examen: str

class TipoExamenUpdate(BaseModel):
    nombre_tipo_examen: Optional[str] = None
    descripcion: Optional[str] = None
    is_active: Optional[bool] = None

class TipoExamenOut(CatalogoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_tipo_examen: int
    nombre_tipo_examen: str
    is_active: bool

#RECETAS
class RecetaMedicaBase(BaseModel):
    dosis: Decimal
    frecuencia: str
    duracion_dias: int
    instrucciones_administracion: Optional[str] = None
    
    generar_tarea_automatica: bool = False
    frecuencia_cron: Optional[str] = None 
    
    usuario_asignado_id: Optional[int] = None

    @model_validator(mode='after')
    def check_cron_logic(self):
        return self

class RecetaMedicaCreate(RecetaMedicaBase):
    producto_id: int
    unidad_medida_id: Optional[int] = None

class RecetaMedicaUpdate(BaseModel):
    producto_id: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    dosis: Optional[Decimal] = None
    frecuencia: Optional[str] = None
    duracion_dias: Optional[int] = None
    instrucciones_administracion: Optional[str] = None
    generar_tarea_automatica: Optional[bool] = None
    frecuencia_cron: Optional[str] = None
    usuario_asignado_id: Optional[int] = None

class RecetaMedicaOut(RecetaMedicaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_receta: int
    created_at: datetime
    
    producto: ProductoOut
    unidad_medida: Optional[UnidadMedidaOut] = None
    usuario_asignado: Optional[UserOut] = None


#PROCEDIMIENTO
class ProcedimientoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_programada: Optional[datetime] = None

class ProcedimientoCreate(ProcedimientoBase):
    pass

class ProcedimientoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    estado: Optional[str] = None

class ProcedimientoOut(ProcedimientoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_procedimiento: int
    estado: str


#EXAMENES
class ResultadoExamenCreate(BaseModel):
    conclusiones: Optional[str] = None

class ResultadoExamenUpdate(BaseModel):
    conclusiones: Optional[str] = None

class ResultadoExamenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_resultado: int
    fecha_resultado: datetime
    conclusiones: Optional[str]
    archivo_url: str


class OrdenExamenBase(BaseModel):
    instrucciones: Optional[str] = None

class OrdenExamenCreate(OrdenExamenBase):
    tipo_examen_id: int

class OrdenExamenUpdate(BaseModel):
    instrucciones: Optional[str] = None
    estado: Optional[str] = None # Solicitado, Completado

class OrdenExamenOut(OrdenExamenBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_orden: int
    estado: str
    created_at: datetime
    
    tipo_examen: TipoExamenOut
    resultados: List[ResultadoExamenOut] = []

#HISTORIAL MEDICO
class HistorialMedicoBase(BaseModel):
    anamnesis: Optional[str] = None
    peso_actual: Optional[Decimal] = None
    temperatura: Optional[Decimal] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    examen_fisico_obs: Optional[str] = None
    diagnostico_presuntivo: Optional[str] = None
    diagnostico_definitivo: Optional[str] = None

class HistorialMedicoCreate(HistorialMedicoBase):
    animal_id: int
    tipo_atencion_id: int

class HistorialMedicoUpdate(HistorialMedicoBase):
    estado: Optional[bool] = None # 1 Abierto, 0 Cerrado
    tipo_atencion_id: Optional[int] = None

class HistorialMedicoOut(HistorialMedicoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_historial: int
    fecha_atencion: datetime
    estado: bool 
    
    veterinario: UserOut
    animal: AnimalOut
    tipo_atencion: TipoAtencionOut
    
    recetas: List[RecetaMedicaOut] = []
    ordenes_examen: List[OrdenExamenOut] = []
    procedimientos: List[ProcedimientoOut] = []