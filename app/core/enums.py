from enum import Enum

class UserRole(str, Enum):
    ADMINISTRADOR = "administrador"
    VETERINARIO = "veterinario"
    CUIDADOR = "cuidador"
    VISITANTE = "visitante"
