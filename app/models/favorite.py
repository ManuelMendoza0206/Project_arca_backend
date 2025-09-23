from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class AnimalFavorite(Base):
    __tablename__ = "animal_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="favorites")
    animal = relationship("Animal", back_populates="favorites")

    __table_args__ = (UniqueConstraint("user_id", "animal_id", name="uq_user_animal_favorite"),)
