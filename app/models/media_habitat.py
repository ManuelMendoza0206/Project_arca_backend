from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class MediaHabitat(Base):
    __tablename__ = "media_habitats"

    id = Column(Integer, primary_key=True, index=True)
    habitat_id = Column(Integer, ForeignKey("habitats.id"), nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(String, nullable=True)
    mime_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    habitat = relationship("Habitat")
