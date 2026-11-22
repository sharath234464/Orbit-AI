from datetime import datetime, timezone

class ChatRepository:
    def __init__(self, database):
        self.conversations = database["conversations"]

    async def ensure_indexes(self):
        await self.conversations.create_index([("user_id", 1), ("updated_at", -1)])

    async def save_turn(self, user_id, conversation_id, user_message, assistant_message, metadata):
        from bson import ObjectId
        now = datetime.now(timezone.utc)
        await self.conversations.update_one(
            {"conversation_id": conversation_id, "user_id": user_id},
            {"$setOnInsert": {"conversation_id": conversation_id, "user_id": user_id, "created_at": now},
             "$set": {"updated_at": now, "last_provider": metadata["provider"], "last_model": metadata["model"]},
             "$push": {"messages": {"$each": [
                 {"role": "user", "content": user_message, "created_at": now},
                 {"role": "assistant", "content": assistant_message, "created_at": now, "provider": metadata["provider"], "model": metadata["model"]},
             ]}}},
            upsert=True,
        )

    async def list_for_user(self, user_id, limit=30):
        cursor = self.conversations.find({"user_id": user_id}, {"_id": 0, "conversation_id": 1, "created_at": 1, "updated_at": 1, "last_provider": 1, "last_model": 1, "messages": {"$slice": -2}}).sort("updated_at", -1).limit(limit)
        rows = await cursor.to_list(length=limit)
        for row in rows:
            row["title"] = next((m.get("content", "") for m in row.get("messages", []) if m.get("role") == "user"), "New conversation")[:72]
            for key in ("created_at", "updated_at"):
                if row.get(key): row[key] = row[key].isoformat()
        return rows
