from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.db_handler.mongodb import MongoDB
from app.exception.handlers import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.provider.registry import build_provider_registry
from app.repository.usage_repository import UsageRepository
from app.repository.auth_repository import AuthRepository
from app.repository.chat_repository import ChatRepository
from app.service.gateway_service import GatewayService
from app.service.auth_service import AuthService
from app.router.app_router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    await MongoDB.connect(settings.mongodb_uri, settings.mongodb_database)
    repository = UsageRepository(MongoDB.database)
    auth_repository = AuthRepository(MongoDB.database)
    chat_repository = ChatRepository(MongoDB.database)
    await repository.ensure_indexes()
    await auth_repository.ensure_indexes()
    await chat_repository.ensure_indexes()
    providers = build_provider_registry(settings)
    await repository.sync_model_registry(providers, settings)
    app.state.settings = settings
    app.state.mongodb = MongoDB.database
    app.state.providers = providers
    app.state.usage_repository = repository
    app.state.auth_service = AuthService(auth_repository, settings)
    app.state.chat_repository = chat_repository
    app.state.gateway_service = GatewayService(providers, repository, settings, chat_repository)
    try:
        yield
    finally:
        for provider in providers.values():
            await provider.close()
        await MongoDB.close()

app = FastAPI(
    title="Intelligent LLM Gateway",
    version="1.0.0",
    description="Agentic multi-model LLM gateway with authentication, MongoDB persistence, and task-aware routing.",
    lifespan=lifespan,
)
app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
