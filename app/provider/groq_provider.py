
from openai import AsyncOpenAI

from app.provider.base import BaseProvider
from app.prompt.system_prompts import SYSTEM_PROMPT


class GroqProvider(BaseProvider):
    """Groq provider using its OpenAI-compatible chat completions API."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    async def generate(
        self,
        messages,
        model: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict:
        payload = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + [message.model_dump() for message in messages]

        response = await self.client.chat.completions.create(
            model=model,
            messages=payload,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )

        usage = response.usage

        return {
            "model": response.model or model,
            "content": response.choices[0].message.content or "",
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }

    async def close(self):
        await self.client.close()
