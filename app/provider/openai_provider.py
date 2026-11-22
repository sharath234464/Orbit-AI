from openai import AsyncOpenAI
from app.provider.base import BaseProvider
from app.prompt.system_prompts import SYSTEM_PROMPT

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, messages, model, temperature, max_output_tokens):
        payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [m.model_dump() for m in messages]
        response = await self.client.chat.completions.create(model=model, messages=payload, temperature=temperature, max_tokens=max_output_tokens)
        usage = response.usage
        return {"model": response.model or model, "content": response.choices[0].message.content or "", "input_tokens": usage.prompt_tokens if usage else 0, "output_tokens": usage.completion_tokens if usage else 0, "total_tokens": usage.total_tokens if usage else 0}

    async def close(self):
        await self.client.close()
