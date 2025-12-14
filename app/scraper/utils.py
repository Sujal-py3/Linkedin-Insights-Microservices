import random
import asyncio

async def random_delay(min_seconds=1, max_seconds=3):
    """Wait for a random amount of time to mimic human behavior."""
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))
