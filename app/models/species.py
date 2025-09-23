from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String(150), nullable=False)
    common_name = Column(String(150), nullable=False)
    phylum = Column(String(100), nullable=True)
    class_name = Column(String(100), nullable=True)
    order = Column(String(100), nullable=True)
    family = Column(String(100), nullable=True)
    genus = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
