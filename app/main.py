import sys
import asyncio

# Fix for Playwright on Windows: https://github.com/microsoft/playwright-python/issues/294
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.db.mongodb import mongodb
from app.db.redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongodb.connect()
    redis_client.connect()
    yield
    # Shutdown
    mongodb.close()
    await redis_client.close()

app = FastAPI(
    title="Linkedin Insights Microservice",
    description="API to scrape and serve LinkedIn page insights.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Linkedin Insights Microservice is running"}
