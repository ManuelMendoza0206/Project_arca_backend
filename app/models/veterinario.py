from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, Numeric, func, CheckConstraint
)
from sqlalchemy.orm import relationship, validates
from app.db.base import Base

class TipoAtencion(Base):
    __tablename__ = "tipo_atencion"

    id_tipo_atencion = Column(Integer, primary_key=True, index=True)
    nombre_tipo_atencion = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    historiales = relationship("HistorialMedico", back_populates="tipo_atencion")

class TipoExamen(Base):
    __tablename__ = "tipo_examen"

    id_tipo_examen = Column(Integer, primary_key=True, index=True)
    nombre_tipo_examen = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    ordenes = relationship("OrdenExamen", back_populates="tipo_examen")


class HistorialMedico(Base):
    __tablename__ = "historial_medico"

    id_historial = Column(Integer, primary_key=True, index=True)
    
    animal_id = Column(Integer, ForeignKey("animals.id_animal"), nullable=False, index=True)
    veterinario_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tipo_atencion_id = Column(Integer, ForeignKey("tipo_atencion.id_tipo_atencion"), nullable=False)

    fecha_atencion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    anamnesis = Column(Text, nullable=True)

    peso_actual = Column(Numeric(10, 2), nullable=True)
    temperatura = Column(Numeric(5, 2), nullable=True)
    frecuencia_cardiaca = Column(Integer, nullable=True)
    frecuencia_respiratoria = Column(Integer, nullable=True)
    examen_fisico_obs = Column(Text, nullable=True)

    diagnostico_presuntivo = Column(Text, nullable=True)
    diagnostico_definitivo = Column(Text, nullable=True)

    estado = Column(Boolean, default=True, nullable=False) # 1 (Abierto/En tratamiento), 0 (Cerrado/Alta)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    animal = relationship("Animal", back_populates="historiales") 
    veterinario = relationship("User", back_populates="historiales_creados")
    tipo_atencion = relationship("TipoAtencion", back_populates="historiales")
    
    recetas = relationship("RecetaMedica", back_populates="historial", cascade="all, delete-orphan")
    ordenes_examen = relationship("OrdenExamen", back_populates="historial", cascade="all, delete-orphan")
    procedimientos = relationship("ProcedimientoMedico", back_populates="historial", cascade="all, delete-orphan")

class OrdenExamen(Base):
    __tablename__ = "orden_examen"

    id_orden = Column(Integer, primary_key=True, index=True)
    historial_medico_id = Column(Integer, ForeignKey("historial_medico.id_historial"), nullable=False)
    tipo_examen_id = Column(Integer, ForeignKey("tipo_examen.id_tipo_examen"), nullable=False)
    
    instrucciones = Column(Text, nullable=True)
    estado = Column(String(20), default="Solicitado", nullable=False) #"Solicitado", "Completado", "Cancelado"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    historial = relationship("HistorialMedico", back_populates="ordenes_examen")
    tipo_examen = relationship("TipoExamen", back_populates="ordenes")
    resultados = relationship("ResultadoExamen", back_populates="orden", cascade="all, delete-orphan")


class ResultadoExamen(Base):
    __tablename__ = "resultado_examen"

    id_resultado = Column(Integer, primary_key=True, index=True)
    orden_examen_id = Column(Integer, ForeignKey("orden_examen.id_orden"), nullable=False)
    
    fecha_resultado = Column(DateTime(timezone=True), server_default=func.now())
    conclusiones = Column(Text, nullable=True)

    archivo_url = Column(String(2048), nullable=False)
    public_id = Column(String(255), nullable=True)

    orden = relationship("OrdenExamen", back_populates="resultados")

class RecetaMedica(Base):
    __tablename__ = "receta_medica"

    id_receta = Column(Integer, primary_key=True, index=True)
    historial_medico_id = Column(Integer, ForeignKey("historial_medico.id_historial"), nullable=False)
    
    producto_id = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    unidad_medida_id = Column(Integer, ForeignKey("unidad_medida.id_unidad"), nullable=True)
    
    dosis = Column(Numeric(10, 2), nullable=False)
    frecuencia = Column(String(100), nullable=False)
    duracion_dias = Column(Integer, nullable=False)
    
    instrucciones_administracion = Column(Text, nullable=True)
    
    generar_tarea_automatica = Column(Boolean, default=False, nullable=False)
    frecuencia_cron = Column(String(100), nullable=True)
    
    usuario_asignado_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    historial = relationship("HistorialMedico", back_populates="recetas")
    producto = relationship("Producto", back_populates="recetas_asociadas")
    unidad_medida = relationship("UnidadMedida", back_populates="recetas_asociadas")
    usuario_asignado = relationship("User", back_populates="recetas_asignadas")

    __table_args__ = (
        CheckConstraint(
            '(generar_tarea_automatica = FALSE) OR (frecuencia_cron IS NOT NULL)', 
            name='chk_receta_cron_obligatorio'
        ),
    )

    @validates('dosis', 'duracion_dias')
    def validate_positive(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f"El campo {key} debe ser mayor a 0")
        return value


class ProcedimientoMedico(Base):
    __tablename__ = "procedimiento_medico"

    id_procedimiento = Column(Integer, primary_key=True, index=True)
    historial_medico_id = Column(Integer, ForeignKey("historial_medico.id_historial"), nullable=False)
    
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_programada = Column(DateTime(timezone=True), nullable=True)
    
    estado = Column(String(20), default="Pendiente", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    historial = relationship("HistorialMedico", back_populates="procedimientos")