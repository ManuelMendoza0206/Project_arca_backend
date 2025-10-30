from sqlalchemy.orm import Session
from redis.asyncio import Redis
from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.db.cache import get_cache_client
from fastapi import Depends


MAX_FAILED_ATTEMPTS = 5
# tiempo bloqueo
LOCKOUT_DURATION_MINUTES = 30 
# Cuanto va recordar redis el tiempo de bloqueo
FAILED_ATTEMPTS_TTL_SECONDS = 3600

FAILED_LOGIN_PREFIX = "failed_login:"


def _get_redis_key(email: str) -> str:
    """Generar clave redis"""
    return f"{FAILED_LOGIN_PREFIX}{email.lower().strip()}"


async def increment_login_failure(
    email: str,
    cache: Redis = Depends(get_cache_client)
):
    """
    Incrementa el contador de fallos en Redis para un email
    """
    if not cache:
        print("Advertencia: Cliente Redis no disponible Omitiendo incremento de fallos")
        return

    key = _get_redis_key(email)
    
    async with cache.pipeline() as pipe:
        await pipe.incr(key)
        await pipe.expire(key, FAILED_ATTEMPTS_TTL_SECONDS)
        await pipe.execute()


async def get_login_failures(
    email: str,
    cache: Redis = Depends(get_cache_client)
) -> int:
    """
    Obtiene el numero de fallos que llevamos
    """
    if not cache:
        print("Advertencia: Cliente Redis no disponible asumo 0 fallos🙌")
        return 0

    key = _get_redis_key(email)
    failures = await cache.get(key)
    
    return int(failures) if failures else 0


async def clear_login_failures(
    email: str,
    cache: Redis = Depends(get_cache_client)
):
    """
    Limpia el contador de fallos de Redis
    """
    if not cache:
        print("Advertencia: Cliente Redis no disponible Omitiendo limpieza de fallos🙌")
        return
        
    key = _get_redis_key(email)
    await cache.delete(key)


def lock_account(db: Session, user: User) -> None:
    """
    Escribe el bloqueo oficial
    """
    lock_until_time = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    
    user.locked_until = lock_until_time
    db.add(user)
    db.commit()


def is_account_locked(user: User) -> bool:
    """
    Verifica si la cuenta esta blqoeuada
    """
    if not user.locked_until:
        return False

    return user.locked_until > datetime.now(timezone.utc)