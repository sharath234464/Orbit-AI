
from datetime import datetime, timezone

from app.enums.request_status import RequestStatus


class UsageRepository:
    def __init__(self, database):
        self.database = database
        self.request_logs = database["request_logs"]
        self.usage_records = database["usage_records"]
        self.model_registry = database["model_registry"]

    async def ensure_indexes(self):
        await self.request_logs.create_index("request_id", unique=True)
        await self.usage_records.create_index("request_id")
        await self.usage_records.create_index("created_at")
        await self.model_registry.create_index("provider", unique=True)

    async def save_request_log(self, record: dict):
        payload = {
            **record,
            "created_at": datetime.now(timezone.utc),
        }

        await self.request_logs.update_one(
            {"request_id": record["request_id"]},
            {"$set": payload},
            upsert=True,
        )

    async def save_usage(self, record: dict):
        payload = {
            **record,
            "created_at": datetime.now(timezone.utc),
        }

        await self.usage_records.insert_one(payload)

    async def dashboard_stats(self):
        total = await self.request_logs.count_documents({})
        successful = await self.request_logs.count_documents(
            {"status": RequestStatus.SUCCESS.value}
        )
        failed = await self.request_logs.count_documents(
            {"status": RequestStatus.FAILED.value}
        )

        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "tokens": {"$sum": "$total_tokens"},
                }
            }
        ]

        result = await self.usage_records.aggregate(
            pipeline
        ).to_list(length=1)

        return {
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": failed,
            "total_tokens": result[0]["tokens"] if result else 0,
        }

    async def recent_usage(self, limit: int = 20):
        cursor = (
            self.usage_records.find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def sync_model_registry(self, providers: dict, settings):
        model_map = {
            "openai": settings.openai_model,
            "anthropic": settings.anthropic_model,
            "google": settings.google_model,
            "groq": settings.groq_model,
        }

        for name, model in model_map.items():
            await self.model_registry.update_one(
                {"provider": name},
                {
                    "$set": {
                        "provider": name,
                        "model": model,
                        "enabled": name in providers,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )
