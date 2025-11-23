from datetime import date
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Enum as SQLAlchemyEnum, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app.db.base import Base
from app.core.enums import AnimalState

from sqlalchemy.ext.hybrid import hybrid_property

class Especie(Base):
    __tablename__ = "especies"

    id_especie = Column(Integer, primary_key=True)
    nombre_cientifico = Column(String(100), nullable=False, unique=True, index=True)
    nombre_especie = Column("nombre", String(100), nullable=False)
    filo = Column(String(100), nullable=False)
    clase = Column(String(100), nullable=False)
    orden = Column(String(100), nullable=False)
    familia = Column(String(100), nullable=False)
    descripcion_especie = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    animales = relationship("Animal", back_populates="especie")
    #tarea
    dieta = relationship("Dieta", back_populates="especie", uselist=False)

    @validates('nombre_especie', 'nombre_cientifico', 'filo', 'clase', 'orden', 'familia', 'genero')
    def normalize_text_fields(self, key, value):
        if isinstance(value, str):
            return value.strip()
        return value



class Habitat(Base):
    __tablename__ = "habitats"

    id_habitat = Column(Integer, primary_key=True, index=True)
    nombre_habitat = Column(String(50), nullable=False)
    tipo_habitat = Column(String(80), nullable=False)
    descripcion_habitat = Column(Text, nullable=False)
    condiciones_climaticas = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    animales = relationship("Animal", back_populates="habitat")
    media = relationship("MediaHabitat", back_populates="habitat", cascade="all, delete-orphan")
    #tareas
    tareas = relationship("Tarea", back_populates="habitat")
    tareas_recurrentes = relationship("TareaRecurrente", back_populates="habitat")
    registros_alimentacion = relationship("RegistroAlimentacion", back_populates="habitat")
    consumo_inventarios = relationship("DetalleSalida", back_populates="habitat")
    @validates('nombre_habitat', 'tipo_habitat')
    def normalize_text_fields(self, key, value):
        if isinstance(value, str):
            return value.strip()
        return value


class Animal(Base):
    __tablename__ = "animals"

    id_animal = Column(Integer, primary_key=True)
    nombre_animal = Column(String(100), nullable=False, index=True)
    especie_id = Column("especies_id_especie", Integer, ForeignKey("especies.id_especie"), nullable=False)
    genero = Column(Boolean, nullable=False) # True: Macho, False: Hembra
    fecha_nacimiento = Column(Date, nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    procedencia_animal = Column(String(300), nullable=False)
    estado_operativo = Column("estado_operativo", SQLAlchemyEnum(AnimalState), nullable=False)
    habitat_id = Column("habitats_id_habitat", Integer, ForeignKey("habitats.id_habitat"), nullable=False)
    es_publico = Column(Boolean, nullable=False, default=True)
    descripcion = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    especie = relationship("Especie", back_populates="animales")
    habitat = relationship("Habitat", back_populates="animales")
    media = relationship("MediaAnimal", back_populates="animal", cascade="all, delete-orphan")
    favorited_by_users = relationship("AnimalFavorito", back_populates="animal", cascade="all, delete-orphan")
    #inventario
    consumo_inventario = relationship("DetalleSalida", back_populates="animal")
    @hybrid_property
    def age(self) -> int | None:
        if not self.fecha_nacimiento:
            return None
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    #tareas
    tareas = relationship("Tarea", back_populates="animal")
    tareas_recurrentes = relationship("TareaRecurrente", back_populates="animal")
    dieta = relationship("Dieta", back_populates="animal", uselist=False)
    registros_alimentacion = relationship("RegistroAlimentacion", back_populates="animal")

    @age.expression
    def age(cls):
        if not hasattr(cls, 'fecha_nacimiento'):
            return None
        return func.floor(
            func.extract('epoch', (func.now() - cls.fecha_nacimiento)) / 31557600
        )
    #PROBANDO COSITAS
    #un CheckConstraint impone la regla a nivel de base de datos, haciéndola imposible de saltar
    __table_args__ = (
        CheckConstraint('fecha_ingreso >= fecha_nacimiento', name='_fecha_ingreso_no_antes_nacimiento'),
    )


class MediaAnimal(Base):
    __tablename__ = "media_animal"

    id_media_animal = Column(Integer, primary_key=True, autoincrement=True)
    animal_id = Column("animals_id_animal", Integer, ForeignKey("animals.id_animal"), nullable=False)
    tipo_medio = Column(Boolean, nullable=False)#1 imagen 0 video
    url_animal = Column(String(2048), nullable=False)
    public_id = Column(String(100), nullable=True)
    titulo_media_animal = Column(String(150), nullable=False)
    descripcion_media_animal = Column(Text, nullable=True)

    animal = relationship("Animal", back_populates="media")

class MediaHabitat(Base):
    __tablename__ = "media_habitats"

    id_media_habitat = Column(Integer, primary_key=True, autoincrement=True)
    habitat_id = Column("habitats_id_habitat", Integer, ForeignKey("habitats.id_habitat"), nullable=False)
    url_habitat = Column(String(2048), nullable=False)
    public_id = Column(String(100), nullable=True)
    titulo_media_habitat = Column(String(150), nullable=False)
    descripcion_media_habitat = Column(Text, nullable=True)
    tipo_medio = Column(Boolean, nullable=False)#1 imagen 0 video
    habitat = relationship("Habitat", back_populates="media")

class AnimalFavorito(Base):
    __tablename__ = "animalfavorito"

    id_animal_favorito = Column("id_animal_favorito", Integer, primary_key=True, autoincrement=True)
    fecha_guardado = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    animal_id = Column(Integer, ForeignKey("animals.id_animal"), nullable=False)

    usuario = relationship("User", back_populates="favorited_by_users")
    animal = relationship("Animal", back_populates="favorited_by_users")
    __table_args__ = (
        UniqueConstraint('usuario_id', 'animal_id', name='_usuario_animal_uc'),
    )