from enum import Enum

class UserRole(str, Enum):
    ADMINISTRADOR = "administrador"
    VETERINARIO = "veterinario"
    CUIDADOR = "cuidador"
    VISITANTE = "visitante"

class AnimalState(str, Enum):
    SALUDABLE = "Saludable"
    EN_TRATAMIENTO = "En tratamiento"
    EN_CUARENTENA = "En cuarentena"
    TRASLADADO = "Trasladado"
    FALLECIDO = "Fallecido"