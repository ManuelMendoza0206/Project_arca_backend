from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from app.schemas.user import UserOut 
from app.schemas.inventario import ProductoOut, ProveedorOut
from app.schemas.animal import AnimalOut, HabitatOut

#Schemas creacion
class DetalleEntradaCreate(BaseModel):
    producto_id: int
    cantidad_entrada: Decimal
    fecha_caducidad: date
    lote: str

class EntradaInventarioCreate(BaseModel):
    proveedor_id: int
    detalles: List[DetalleEntradaCreate] 

class DetalleEntradaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_detalle_entrada: int
    producto_id: int
    cantidad_entrada: Decimal
    fecha_caducidad: date
    lote: str
    
    producto: ProductoOut 

class EntradaInventarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_entrada_inventario: int
    fecha_entrada: datetime
    usuario_id: int
    proveedor_id: int

    usuario: UserOut
    proveedor: ProveedorOut
    detalles: List[DetalleEntradaOut]


#tipo salidas
class TipoSalidaBase(BaseModel):
    nombre_tipo_salida: str
    descripcion_tipo_salida: Optional[str] = None

class TipoSalidaCreate(TipoSalidaBase):
    pass

class TipoSalidaUpdate(BaseModel):
    nombre_tipo_salida: Optional[str] = None
    descripcion_tipo_salida: Optional[str] = None
    is_active: Optional[bool] = None

class TipoSalidaOut(TipoSalidaBase):
    model_config = ConfigDict(from_attributes=True)
    id_tipo_salida: int
    nombre_tipo_salida: str
    is_active: bool

#SALIDAS
class DetalleSalidaCreate(BaseModel):
    producto_id: int
    cantidad_salida: Decimal
    animal_id: Optional[int] = None
    habitat_id: Optional[int] = None

    @model_validator(mode='after')
    def check_destiny(self):
        if not self.animal_id and not self.habitat_id:
            raise ValueError('Debe especificar un animal_id o un habitat_id')
        if self.animal_id and self.habitat_id:
            raise ValueError('No puede especificar animal y habitat al mismo tiempo')
        return self

class SalidaInventarioCreate(BaseModel):
    tipo_salida: int
    detalles: List[DetalleSalidaCreate]


class DetalleSalidaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_detalle_salida: int
    cantidad_salida: Decimal
    producto: ProductoOut 
    animal: Optional[AnimalOut] = None
    habitat: Optional[HabitatOut] = None

class SalidaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_salida: int
    fecha_salida: datetime
    
    tipo_salida: TipoSalidaOut
    usuario: UserOut
    detalles: List[DetalleSalidaOut]
