from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        print("Connected to MongoDB")

    def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

mongodb = MongoDB()

def get_db():
    return mongodb.db
