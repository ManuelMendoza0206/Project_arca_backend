from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base
#Prueba
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.role import Role
from sqlalchemy.sql import select
from app.core.enums import UserRole
#prueba 2
from sqlalchemy.orm import validates
import re
#SQLaclchemy as ORM

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    #unique=True
    email = Column(String(200), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    photo_url = Column(String(2048), nullable=True) #estandar

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    role = relationship("Role", back_populates="users")
    encuestas_creadas = relationship("Encuesta", back_populates="usuario_creador")
    participaciones_encuestas = relationship("ParticipacionEncuesta", back_populates="usuario")
    trivias_creadas = relationship("Trivia", back_populates="usuario")
    participaciones_trivia = relationship("ParticipacionTrivia", back_populates="usuario")   
    animales_favoritos = relationship("AnimalFavorito", back_populates="usuario", cascade="all, delete-orphan")

    #Pruebas
    #propeidades hibridas
    @hybrid_property
    def is_admin(self):

        return self.role.name == UserRole.ADMINISTRADOR.value

    @is_admin.expression
    def is_admin(cls):
        # subconsulta que revisa el nombre del rol
        return (
            select([Role.name])
            .where(Role.id == cls.role_id)
            .as_scalar()
        ) == UserRole.ADMINISTRADOR.value
    
    #validacion
    @validates('email')
    def validate_and_normalize_email(self, key, email_address):
        if not email_address:
            raise ValueError("El email no puede estar vacio")
              
        normalized_email = email_address.lower().strip()

        if '@' not in normalized_email or '.' not in normalized_email.split('@')[-1]:
             raise ValueError(f"Email no valido: '{email_address}'")
        return normalized_email

    @validates('username')
    def validate_and_normalize_username(self, key, username):
        if not username:
            raise ValueError("El nombre de usuario no puede estar vacio")

        normalized_username = username.strip()
        #solo alfanumerico
        #if not re.match("^[a-zA-Z0-9_.-]+$", normalized_username):
        #     raise ValueError("El nombre de usuario solo puede contener letras, numeros, _, . y -")

        return normalized_username