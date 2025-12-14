import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "linkedin_insights")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
