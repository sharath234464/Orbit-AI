
from app.agent.routing_rules import (
    CODING_KEYWORDS,
    REASONING_KEYWORDS,
    TASK_PREFERENCES,
)


def classify_task_node(state: dict) -> dict:
    """Classify the conversation into a lightweight task category."""
    user_text = []

    for message in state.get("messages", []):
        role = (
            message.get("role", "")
            if isinstance(message, dict)
            else getattr(message, "role", "")
        )
        content = (
            message.get("content", "")
            if isinstance(message, dict)
            else getattr(message, "content", "")
        )

        if role == "user" and isinstance(content, str):
            user_text.append(content)

    text = " ".join(user_text).lower()

    if any(word in text for word in CODING_KEYWORDS):
        task = "coding"
    elif any(word in text for word in REASONING_KEYWORDS):
        task = "reasoning"
    elif len(text.split()) <= 20:
        task = "simple"
    else:
        task = "general"

    return {"task_type": task}


def _configured_model(settings, provider_name: str) -> str:
    model_settings = {
        "openai": settings.openai_model,
        "anthropic": settings.anthropic_model,
        "google": settings.google_model,
        "groq": settings.groq_model,
    }

    model = model_settings.get(provider_name)

    if not model:
        raise ValueError(
            f"No model is configured for provider '{provider_name}'."
        )

    return model


def make_select_provider_node(settings, providers: dict):
    """Select a provider automatically or honor manual model selection."""

    def select_provider(state: dict) -> dict:
        requested = (state.get("requested_model") or "auto").strip()
        enabled = sorted(providers.keys())

        # Manual mode: provider:model-id
        if requested.lower() != "auto":
            if ":" not in requested:
                raise ValueError(
                    "Select a model from the refreshed model list."
                )

            provider_name, model_name = requested.split(":", 1)
            provider_name = provider_name.strip().lower()
            model_name = model_name.strip()

            if provider_name not in providers:
                raise ValueError(
                    f"Provider '{provider_name}' is not enabled. "
                    f"Available providers: {', '.join(enabled) or 'none'}."
                )

            expected_model = _configured_model(settings, provider_name)

            if model_name != expected_model:
                raise ValueError(
                    f"Model '{model_name}' is not configured for "
                    f"'{provider_name}'. Expected '{expected_model}'."
                )

            return {
                "provider_name": provider_name,
                "model_name": model_name,
                "task_type": "manual",
                "routing_reason": (
                    f"User selected {provider_name}:{model_name}."
                ),
            }

        # Best Model mode: use the first available provider for this task.
        task = state.get("task_type", "general")
        preferences = TASK_PREFERENCES.get(
            task, TASK_PREFERENCES["general"]
        )

        provider_name = next(
            (name for name in preferences if name in providers),
            None,
        )

        if not provider_name:
            raise ValueError(
                "No LLM provider is configured. Add a valid API key "
                "to backend/.env and restart the backend."
            )

        model_name = _configured_model(settings, provider_name)

        return {
            "provider_name": provider_name,
            "model_name": model_name,
            "routing_reason": (
                f"Best Model selected {provider_name} for a {task} request."
            ),
        }

    return select_provider


def route_metadata_node(state: dict) -> dict:
    """Reserved for additional routing metadata."""
    return {}
