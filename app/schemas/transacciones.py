from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from app.schemas.user import UserOut 
from app.schemas.inventario import ProductoOut, ProveedorOut
from app.schemas.animal import AnimalOut

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

#SALIDAS
class DetalleSalidaCreate(BaseModel):
    producto_id: int
    cantidad_salida: Decimal
    animal_id: Optional[int] = None

class SalidaInventarioCreate(BaseModel):
    tipo_salida: str
    detalles: List[DetalleSalidaCreate]


class DetalleSalidaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_detalle_salida: int
    cantidad_salida: Decimal
    producto: ProductoOut 
    animal: Optional[AnimalOut] = None

class SalidaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_salida: int
    fecha_salida: datetime
    tipo_salida: str
    
    usuario: UserOut
    detalles: List[DetalleSalidaOut]
