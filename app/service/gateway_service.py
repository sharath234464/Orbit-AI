
import logging
import time
import uuid

from app.agent.graph import build_routing_graph
from app.enums.request_status import RequestStatus
from app.prompt.system_prompts import SYSTEM_PROMPT
from app.schemas.chat_schema import ChatResponse, Usage

logger = logging.getLogger(__name__)


class GatewayService:
    def __init__(self, providers, repository, settings, chat_repository):
        self.providers = providers
        self.repository = repository
        self.settings = settings
        self.chat_repository = chat_repository

        self.routing_graph = build_routing_graph(settings, providers)

    async def chat(self, request, user):
        started = time.perf_counter()
        request_id = str(uuid.uuid4())
        conversation_id = request.conversation_id or str(uuid.uuid4())

        messages = request.messages

        if not any(message.role == "system" for message in messages):
            from app.schemas.chat_schema import ChatMessage

            messages = [
                ChatMessage(role="system", content=SYSTEM_PROMPT)
            ] + list(messages)

        routing_result = {}
        provider_name = "unknown"
        model_name = request.model or "auto"

        try:
            # Select a provider through the LangGraph routing workflow.
            routing_result = await self.routing_graph.ainvoke(
                {
                    "messages": messages,
                    "requested_model": request.model,
                }
            )

            provider_name = routing_result["provider_name"]
            model_name = routing_result["model_name"]

            if provider_name not in self.providers:
                raise ValueError(
                    f"Provider '{provider_name}' is not registered. "
                    f"Registered providers: {list(self.providers.keys())}"
                )

            provider = self.providers[provider_name]

            # Generate the response using the selected provider.
            result = await provider.generate(
                messages,
                model_name,
                request.temperature,
                request.max_output_tokens,
            )

            required_fields = (
                "model",
                "content",
                "input_tokens",
                "output_tokens",
                "total_tokens",
            )

            missing_fields = [
                field for field in required_fields if field not in result
            ]

            if missing_fields:
                raise ValueError(
                    f"Provider '{provider_name}' returned an invalid "
                    f"response. Missing fields: {missing_fields}"
                )

            content = result["content"]

            if not isinstance(content, str) or not content.strip():
                raise ValueError(
                    f"Provider '{provider_name}' returned empty content "
                    f"for model '{model_name}'."
                )

            latency_ms = round(
                (time.perf_counter() - started) * 1000, 2
            )

            common = {
                "request_id": request_id,
                "user_id": user["id"],
                "provider": provider_name,
                "model": result["model"],
                "status": RequestStatus.SUCCESS.value,
                "latency_ms": latency_ms,
                "task_type": routing_result.get(
                    "task_type", "general"
                ),
                "routing_reason": routing_result.get(
                    "routing_reason", ""
                ),
            }

            # Persist request and usage records.
            await self.repository.save_request_log(common)

            await self.repository.save_usage(
                {
                    **common,
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "total_tokens": result["total_tokens"],
                    "estimated_cost_usd": None,
                }
            )

            last_user_message = next(
                (
                    message.content
                    for message in reversed(request.messages)
                    if message.role == "user"
                ),
                "",
            )

            await self.chat_repository.save_turn(
                user["id"],
                conversation_id,
                last_user_message,
                content,
                {
                    "provider": provider_name,
                    "model": result["model"],
                },
            )

            return ChatResponse(
                request_id=request_id,
                conversation_id=conversation_id,
                model=result["model"],
                provider=provider_name,
                content=content,
                usage=Usage(
                    input_tokens=result["input_tokens"],
                    output_tokens=result["output_tokens"],
                    total_tokens=result["total_tokens"],
                ),
                latency_ms=latency_ms,
                task_type=routing_result.get("task_type", "general"),
                routing_reason=routing_result.get(
                    "routing_reason", ""
                ),
            )

        except Exception as exc:
            latency_ms = round(
                (time.perf_counter() - started) * 1000, 2
            )

            # Log the original exception and traceback for diagnosis.
            logger.exception(
                "Chat generation failed | request_id=%s | "
                "provider=%s | model=%s | error_type=%s | error=%s",
                request_id,
                provider_name,
                model_name,
                type(exc).__name__,
                str(exc),
            )

            # Record the failed request without hiding the original error.
            try:
                await self.repository.save_request_log(
                    {
                        "request_id": request_id,
                        "user_id": user["id"],
                        "provider": provider_name,
                        "model": model_name,
                        "status": RequestStatus.FAILED.value,
                        "latency_ms": latency_ms,
                        "error_type": type(exc).__name__,
                        "task_type": routing_result.get(
                            "task_type", "unknown"
                        ),
                    }
                )
            except Exception:
                logger.exception(
                    "Could not persist failed request | request_id=%s",
                    request_id,
                )

            # Preserve existing exception handling in the API layer.
            raise
