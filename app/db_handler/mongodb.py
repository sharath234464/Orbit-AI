from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    client = None
    database = None

    @classmethod
    async def connect(cls, uri: str, database_name: str):
        cls.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await cls.client.admin.command("ping")
        cls.database = cls.client[database_name]

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
        cls.client = None
        cls.database = None
