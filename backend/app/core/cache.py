from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi import FastAPI
import os

async def init_redis(app: FastAPI):
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    
    redis = aioredis.from_url(
        f"redis://{redis_host}:{redis_port}",
        password=redis_password,
        encoding="utf8",
        decode_responses=True
    )
    
    FastAPICache.init(RedisBackend(redis), prefix="hospital-cache")

def cache(expire: int = 60):
    return FastAPICache.cache(expire=expire)