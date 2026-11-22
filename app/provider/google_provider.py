from google import genai
from google.genai import types
from app.provider.base import BaseProvider
from app.prompt.system_prompts import SYSTEM_PROMPT

class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def generate(self, messages, model, temperature, max_output_tokens):
        system_parts = [SYSTEM_PROMPT] + [m.content for m in messages if m.role == "system"]
        contents = [types.Content(role=("model" if m.role == "assistant" else "user"), parts=[types.Part(text=m.content)]) for m in messages if m.role != "system"]
        response = await self.client.aio.models.generate_content(model=model, contents=contents, config=types.GenerateContentConfig(system_instruction="\\n\\n".join(system_parts), temperature=temperature, max_output_tokens=max_output_tokens))
        usage = getattr(response, "usage_metadata", None)
        inp = getattr(usage, "prompt_token_count", 0) or 0
        out = getattr(usage, "candidates_token_count", 0) or 0
        return {"model": model, "content": response.text or "", "input_tokens": inp, "output_tokens": out, "total_tokens": inp + out}

    async def close(self):
        await self.client.aio.aclose()
