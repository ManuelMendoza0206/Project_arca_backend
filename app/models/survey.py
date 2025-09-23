from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Encuesta(Base):
    __tablename__ = "encuestas"

    id_encuesta = Column("id_encuesta", Integer, primary_key=True, autoincrement=True)
    titulo = Column("titulo", String(100), nullable=False)
    descripcion = Column("descripcion", Text, nullable=False)
    fecha_inicio = Column("fecha_inicio", DateTime(timezone=True), nullable=False)
    fecha_fin = Column("fecha_fin", DateTime(timezone=True), nullable=True)
    usuario_creador_id = Column("usuario_creador_id", Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column("is_active", Boolean, nullable=False, default=True)

    usuario_creador = relationship("User", back_populates="encuestas_creadas")
    temas = relationship("EncuestaTema", back_populates="encuesta", cascade="all, delete-orphan")
    preguntas = relationship("PreguntaEncuesta", back_populates="encuesta", cascade="all, delete-orphan")
    participaciones = relationship("ParticipacionEncuesta", back_populates="encuesta", cascade="all, delete-orphan")


class EncuestaTema(Base):
    __tablename__ = "encuesta_tema"

    id_tema = Column("id_tema", Integer, primary_key=True)
    tipo_tema = Column("tipo_tema", String(50), primary_key=True)
    encuesta_id = Column("encuesta_id", Integer, ForeignKey("encuestas.id_encuesta"), primary_key=True)

    encuesta = relationship("Encuesta", back_populates="temas")


class PreguntaEncuesta(Base):
    __tablename__ = "preguntas_encuesta"

    id_pregunta = Column("id_pregunta", Integer, primary_key=True, autoincrement=True)
    encuesta_id = Column("encuesta_id", Integer, ForeignKey("encuestas.id_encuesta"), nullable=False)
    texto_pregunta = Column("texto_pregunta", String(100), nullable=False)
    es_opcion_unica = Column("es_opcion_unica", Boolean, nullable=False, default=False)
    orden = Column("orden", Integer, nullable=True)
    
    encuesta = relationship("Encuesta", back_populates="preguntas")
    opciones = relationship("OpcionEncuesta", back_populates="pregunta", cascade="all, delete-orphan")
    respuestas = relationship("RespuestaUsuario", back_populates="pregunta")


class OpcionEncuesta(Base):
    __tablename__ = "opcion_encuesta"

    id_opcion = Column("id_opcion", Integer, primary_key=True, autoincrement=True)
    pregunta_id = Column("pregunta_id", Integer, ForeignKey("preguntas_encuesta.id_pregunta"), nullable=False)
    texto_opcion = Column("texto_opcion", String(200), nullable=False)
    orden = Column("orden", Integer, nullable=True)

    pregunta = relationship("PreguntaEncuesta", back_populates="opciones")
    respuestas = relationship("RespuestaUsuario", back_populates="opcion")


class ParticipacionEncuesta(Base):
    __tablename__ = "participaciones_encuesta"

    id_participacion = Column("id_participacion", Integer, primary_key=True)
    encuesta_id = Column("encuesta_id", Integer, ForeignKey("encuestas.id_encuesta"), nullable=False)
    usuario_id = Column("usuario_id", Integer, ForeignKey("users.id"), nullable=False)
    fecha_participacion = Column("fecha_participacion", DateTime(timezone=True), nullable=False)
    completada = Column("completada", Boolean, nullable=False, default=False)
    
    encuesta = relationship("Encuesta", back_populates="participaciones")
    usuario = relationship("User", back_populates="participaciones_encuestas")
    respuestas = relationship("RespuestaUsuario", back_populates="participacion", cascade="all, delete-orphan")


class RespuestaUsuario(Base):
    __tablename__ = "respuesta_usuario"

    id_respuesta = Column("id_respuesta", Integer, primary_key=True, autoincrement=True)
    participacion_id = Column("participacion_id", Integer, ForeignKey("participaciones_encuesta.id_participacion"), nullable=False)
    pregunta_id = Column("pregunta_id", Integer, ForeignKey("preguntas_encuesta.id_pregunta"), nullable=False)
    opcion_id = Column("opcion_id", Integer, ForeignKey("opcion_encuesta.id_opcion"), nullable=True)
    respuesta_texto = Column("respuesta_texto", String(250), nullable=True)

    participacion = relationship("ParticipacionEncuesta", back_populates="respuestas")
    pregunta = relationship("PreguntaEncuesta", back_populates="respuestas")
    opcion = relationship("OpcionEncuesta", back_populates="respuestas")
