from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.db.base import Base

class Trivia(Base):
    __tablename__ = "TRIVIA"

    id_trivia = Column("Id_trivia", Integer, primary_key=True)
    fecha_trivia = Column("Fecha_trivia", DateTime(timezone=True), nullable=False)
    cantidad_preguntas = Column("Cantidad_preguntas", Integer, nullable=False)
    dificultad = Column("Dificultad", String(20), nullable=False)
    usuario_id = Column("USUARIOS_Id_usuario", Integer, ForeignKey("users.id"), nullable=False)

    usuario = relationship("User", back_populates="trivias_creadas")
    participaciones = relationship("ParticipacionTrivia", back_populates="trivia", cascade="all, delete-orphan")


class ParticipacionTrivia(Base):
    __tablename__ = "PARTICIPACIONES_TRIVIA"

    id_participacion_trivia = Column("Id_participacion_trivia", Integer, primary_key=True, autoincrement=True)
    usuario_id = Column("USUARIOS_Id_usuario", Integer, ForeignKey("users.id"), nullable=False)
    aciertos = Column("Aciertos", Integer, nullable=False)
    fecha_trivia = Column("Fecha_trivia", DateTime(timezone=True), nullable=False)
    trivia_id = Column("TRIVIA_Id_trivia", Integer, ForeignKey("TRIVIA.Id_trivia"), nullable=False)

    usuario = relationship("User", back_populates="participaciones_trivia")
    trivia = relationship("Trivia", back_populates="participaciones")
