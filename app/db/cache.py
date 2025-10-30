import redis.asyncio as redis
from app.core.config import settings

try:
    pool = redis.ConnectionPool.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    

    cache_client = redis.Redis.from_pool(pool)
    
    print("Conectado a Redis")

except Exception as e:
    print(f"Error: No se pudo conectar a Redis en {settings.REDIS_URL}")
    print(f"Detalle: {e}")
    cache_client = None

async def get_cache_client() -> redis.Redis | None:
    return cache_client

async def ping_redis():
    if not cache_client:
        return False
    try:
        await cache_client.ping()
        return True
    except Exception:
        return False