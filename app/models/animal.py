from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Enum as SQLAlchemyEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.core.enums import AnimalState

class Especie(Base):
    __tablename__ = "especies"

    id_especie = Column("id_especie", Integer, primary_key=True)
    nombre_cientifico = Column(String(100), nullable=False, unique=True)
    nombre = Column("nombre", String(100), nullable=False)
    filo = Column(String(100), nullable=False)
    clase = Column(String(100), nullable=False)
    orden = Column(String(100), nullable=False)
    familia = Column(String(100), nullable=False)
    genero = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    animales = relationship("Animal", back_populates="especie")


class Habitat(Base):
    __tablename__ = "habitats"

    id_habitat = Column("id_habitat", Integer, primary_key=True)
    nombre_habitat = Column(String(50), nullable=False)
    tipo = Column(String(80), nullable=False)
    descripcion = Column(Text, nullable=False)
    condiciones_climaticas = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    animales = relationship("Animal", back_populates="habitat")
    media = relationship("MediaHabitat", back_populates="habitat", cascade="all, delete-orphan")


class Animal(Base):
    __tablename__ = "animals"

    id_animal = Column("id_animal", Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especie_id = Column("especies_id_especie", Integer, ForeignKey("especies.id_especie"), nullable=False)
    genero = Column(Boolean, nullable=False) # True: Macho, False: Hembra
    fecha_nacimiento = Column(Date, nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    procedencia = Column(String(300), nullable=False)
    estado_operativo = Column("estado_operativo", SQLAlchemyEnum(AnimalState), nullable=False)
    habitat_id = Column("habitats_id_habitat", Integer, ForeignKey("habitats.id_habitat"), nullable=False)
    es_publico = Column(Boolean, nullable=False, default=True)
    descripcion = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    especie = relationship("Especie", back_populates="animales")
    habitat = relationship("Habitat", back_populates="animales")
    media = relationship("MediaAnimal", back_populates="animal", cascade="all, delete-orphan")
    favorited_by_users = relationship("AnimalFavorito", back_populates="animal", cascade="all, delete-orphan")


class MediaAnimal(Base):
    __tablename__ = "media_animal"

    id_media = Column("id_media", Integer, primary_key=True, autoincrement=True)
    animal_id = Column("animals_id_animal", Integer, ForeignKey("animals.id_animal"), nullable=False)
    tipo_medio = Column(String(50))
    url = Column(String(200), nullable=False)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    public_id = Column(String(100), nullable=True)
    animal = relationship("Animal", back_populates="media")

class MediaHabitat(Base):
    __tablename__ = "media_habitats"

    id_media_habitat = Column("id_media_habitat", Integer, primary_key=True, autoincrement=True)
    habitat_id = Column("habitats_id_habitat", Integer, ForeignKey("habitats.id_habitat"), nullable=False)
    url = Column(String(200), nullable=False)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)

    habitat = relationship("Habitat", back_populates="media")

class AnimalFavorito(Base):
    __tablename__ = "animalfavorito"

    id_animal_favorito = Column("id_animal_favorito", Integer, primary_key=True, autoincrement=True)
    fecha_guardado = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    usuario_id = Column("usuarios_id_usuario", Integer, ForeignKey("users.id"), nullable=False)
    animal_id = Column("animals_id_animal", Integer, ForeignKey("animals.id_animal"), nullable=False)

    usuario = relationship("User", back_populates="animales_favoritos")
    animal = relationship("Animal", back_populates="favorited_by_users")