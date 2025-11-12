from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Text, Numeric, Date, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class TipoProducto(Base):
    __tablename__ = "tipo_producto"
    id_tipo_producto = Column(Integer, primary_key=True, index=True)
    nombre_tipo_producto = Column(String(100), nullable=False, unique=True)
    descripcion_tipo_producto = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    productos = relationship("Producto", back_populates="tipo_producto")


class UnidadMedida(Base):
    __tablename__ = "unidad_medida"
    id_unidad = Column(Integer, primary_key=True, index=True)
    nombre_unidad = Column(String(100), nullable=False, unique=True)
    abreviatura = Column(String(20), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    productos = relationship("Producto", back_populates="unidad_medida")


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre_proveedor = Column(String(100), nullable=False, unique=True)
    telefono_proveedor = Column(String(25), nullable=True)
    email_proveedor = Column(String(200), nullable=True, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    entradas_inventario = relationship("EntradaInventario", back_populates="proveedor")


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre_producto = Column(String(200), nullable=False, unique=True)
    descripcion_producto = Column(Text, nullable=True)

    photo_url = Column(String(2048), nullable=True)
    public_id = Column(String(255), nullable=True)

    stock_actual = Column(Numeric(10, 2), default=0, nullable=False)
    stock_minimo = Column(Numeric(10, 2), default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    tipo_producto_id = Column(Integer, ForeignKey("tipo_producto.id_tipo_producto"), nullable=False)
    unidad_medida_id = Column(Integer, ForeignKey("unidad_medida.id_unidad"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tipo_producto = relationship("TipoProducto", back_populates="productos")
    unidad_medida = relationship("UnidadMedida", back_populates="productos")
    stock_lotes = relationship("StockLote", back_populates="producto", cascade="all, delete-orphan")
    detalles_entrada = relationship("DetalleEntrada", back_populates="producto")
    detalles_salida = relationship("DetalleSalida", back_populates="producto")


class StockLote(Base):
    __tablename__ = "stock_lote"
    
    id_stocklote = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id_producto"), nullable=False, index=True)
    lote = Column(String(100), nullable=False, index=True)
    fecha_caducidad = Column(Date, nullable=False, index=True)
    cantidad_disponible = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    producto = relationship("Producto", back_populates="stock_lotes")
    
    __table_args__ = (
        CheckConstraint('cantidad_disponible >= 0', name='chk_cantidad_disponible_no_negativa'),
    )

#Modelos de Transacciones

class EntradaInventario(Base):

    __tablename__ = "entradas_inventario"

    id_entrada_inventario = Column(Integer, primary_key=True, index=True)
    fecha_entrada = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)

    usuario = relationship("User", back_populates="entradas_inventario")
    proveedor = relationship("Proveedor", back_populates="entradas_inventario")
    detalles = relationship("DetalleEntrada", back_populates="entrada", cascade="all, delete-orphan")


class DetalleEntrada(Base):
    __tablename__ = "detalle_entrada"
    
    id_detalle_entrada = Column(Integer, primary_key=True, index=True)
    entrada_id = Column(Integer, ForeignKey("entradas_inventario.id_entrada_inventario"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    
    cantidad_entrada = Column(Numeric(10, 2), nullable=False)
    fecha_caducidad = Column(Date, nullable=False)
    lote = Column(String(100), nullable=False)

    entrada = relationship("EntradaInventario", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_entrada")


class Salida(Base):
    __tablename__ = "salidas"

    id_salida = Column(Integer, primary_key=True, index=True)
    fecha_salida = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tipo_salida = Column(String(100), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    usuario = relationship("User", back_populates="salidas_inventario")
    
    detalles = relationship("DetalleSalida", back_populates="salida", cascade="all, delete-orphan")


class DetalleSalida(Base):
    __tablename__ = "detalle_salidas"
    
    id_detalle_salida = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salidas.id_salida"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id_animal"), nullable=True) 
    
    cantidad_salida = Column(Numeric(10, 2), nullable=False)

    salida = relationship("Salida", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_salida")
    animal = relationship("Animal", back_populates="consumo_inventario")