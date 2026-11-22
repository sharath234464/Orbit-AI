class AuthRepository:
    def __init__(self, database):
        self.users = database["users"]

    async def ensure_indexes(self):
        await self.users.create_index("email", unique=True)

    async def create_user(self, record):
        result = await self.users.insert_one(record)
        record["_id"] = result.inserted_id
        return record

    async def find_by_email(self, email):
        return await self.users.find_one({"email": email.lower().strip()})

    async def find_by_id(self, user_id):
        from bson import ObjectId
        if not ObjectId.is_valid(user_id):
            return None
        return await self.users.find_one({"_id": ObjectId(user_id)})
