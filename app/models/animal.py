from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Text, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    gender = Column(SAEnum(GenderEnum), nullable=False, default=GenderEnum.UNKNOWN)
    birth_date = Column(Date, nullable=True)
    arrival_date = Column(Date, nullable=True)
    origin = Column(String(300), nullable=True)
    operational_status = Column(String(80), nullable=True)
    habitat_id = Column(Integer, ForeignKey("habitats.id"), nullable=True)
    is_public = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    species = relationship("Species")
    habitat = relationship("Habitat", back_populates="animals")
    media = relationship("MediaAnimal", back_populates="animal", cascade="all, delete-orphan")
    favorites = relationship("AnimalFavorite", back_populates="animal", cascade="all, delete-orphan")
