import redis.asyncio as redis

from core.config import settings
from db.redis import get_redis
from main import app


async def override_get_redis():
    pool = redis.ConnectionPool.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}"
    )
    redis_client = redis.Redis.from_pool(pool)
    yield redis_client
    await redis_client.aclose()


app.dependency_overrides[get_redis] = override_get_redis
