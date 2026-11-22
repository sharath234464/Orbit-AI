
from app.provider.openai_provider import OpenAIProvider
from app.provider.anthropic_provider import AnthropicProvider
from app.provider.google_provider import GoogleProvider
from app.provider.groq_provider import GroqProvider


def build_provider_registry(settings):
    providers = {}

    if settings.openai_api_key:
        providers["openai"] = OpenAIProvider(settings.openai_api_key)

    if settings.anthropic_api_key:
        providers["anthropic"] = AnthropicProvider(
            settings.anthropic_api_key
        )

    if settings.google_api_key:
        providers["google"] = GoogleProvider(settings.google_api_key)

    if settings.groq_api_key:
        providers["groq"] = GroqProvider(settings.groq_api_key)

    return providers
