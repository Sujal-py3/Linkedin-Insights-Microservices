import redis.asyncio as aioredis
from app.config import settings

class RedisClient:
    client: aioredis.Redis = None

    def connect(self):
        self.client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        print("Connected to Redis")

    async def close(self):
        if self.client:
            await self.client.close()
            print("Disconnected from Redis")

redis_client = RedisClient()

def get_redis():
    return redis_client.client
