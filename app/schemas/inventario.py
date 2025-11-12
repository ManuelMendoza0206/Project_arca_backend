from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class TipoProductoBase(BaseModel):
    nombre_tipo_producto: str
    descripcion_tipo_producto: Optional[str] = None

class TipoProductoCreate(TipoProductoBase):
    pass

class TipoProductoUpdate(BaseModel):
    nombre_tipo_producto: Optional[str] = None
    descripcion_tipo_producto: Optional[str] = None
    is_active: Optional[bool] = None

class TipoProductoOut(TipoProductoBase):
    model_config = ConfigDict(from_attributes=True)
    id_tipo_producto: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# UnidadMedida
class UnidadMedidaBase(BaseModel):
    nombre_unidad: str
    abreviatura: str

class UnidadMedidaCreate(UnidadMedidaBase):
    pass

class UnidadMedidaUpdate(BaseModel):
    nombre_unidad: Optional[str] = None
    abreviatura: Optional[str] = None
    is_active: Optional[bool] = None

class UnidadMedidaOut(UnidadMedidaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_unidad: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Proveedor Schemas
class ProveedorBase(BaseModel):
    nombre_proveedor: str
    telefono_proveedor: Optional[str] = None
    email_proveedor: Optional[EmailStr] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre_proveedor: Optional[str] = None
    telefono_proveedor: Optional[str] = None
    email_proveedor: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class ProveedorOut(ProveedorBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_proveedor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

#Schemas producto
class ProductoBase(BaseModel):
    nombre_producto: str
    descripcion_producto: Optional[str] = None
    stock_minimo: Decimal = Decimal("0.0")
    tipo_producto_id: int
    unidad_medida_id: int

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre_producto: Optional[str] = None
    descripcion_producto: Optional[str] = None
    stock_minimo: Optional[Decimal] = None
    tipo_producto_id: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_producto: int
    stock_actual: Decimal 
    is_active: bool
    photo_url: Optional[str] = None
    public_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    tipo_producto: TipoProductoOut
    unidad_medida: UnidadMedidaOut