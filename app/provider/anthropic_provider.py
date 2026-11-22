from anthropic import AsyncAnthropic
from app.provider.base import BaseProvider
from app.prompt.system_prompts import SYSTEM_PROMPT

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(self, messages, model, temperature, max_output_tokens):
        systems = [SYSTEM_PROMPT] + [m.content for m in messages if m.role == "system"]
        conversation = [{"role": m.role, "content": m.content} for m in messages if m.role in ("user", "assistant")]
        response = await self.client.messages.create(model=model, system="\\n\\n".join(systems), messages=conversation, temperature=temperature, max_tokens=max_output_tokens)
        content = "\\n".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        usage = response.usage
        return {"model": response.model or model, "content": content, "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens, "total_tokens": usage.input_tokens + usage.output_tokens}

    async def close(self):
        await self.client.close()
