from cryptography.fernet import Fernet
from app.core.config import settings


try:
    cipher_suite = Fernet(settings.TOTP_ENCRYPTION_KEY.encode())
except Exception as e:
    print(f"Error fatal: TOTP_ENCRYPTION_KEY no es valida {e}")
    cipher_suite = None 

def encrypt_data(data: str) -> str:
    if not cipher_suite:
        raise ValueError("El cifrado 2FA no esta configurado")
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not cipher_suite:
        raise ValueError("El cifrado 2FA no esta configrado")
    return cipher_suite.decrypt(encrypted_data.encode()).decode()