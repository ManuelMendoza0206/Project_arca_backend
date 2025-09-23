from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class MediaTypeEnum(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    OTHER = "other"

class MediaAnimal(Base):
    __tablename__ = "media_animals"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    media_type = Column(SAEnum(MediaTypeEnum), nullable=False, default=MediaTypeEnum.IMAGE)
    url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(String, nullable=True)
    mime_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    animal = relationship("Animal", back_populates="media")
