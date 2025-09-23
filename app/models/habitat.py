from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import relationship

class Habitat(Base):
    __tablename__ = "habitats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    climate_conditions = Column(String(250), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    animals = relationship("Animal", back_populates="habitat", cascade="all, delete-orphan")
