
import asyncio

from app.core.config import get_settings
from openai import AsyncOpenAI


async def main():
    settings = get_settings()

    if not settings.groq_api_key:
        print("ERROR: Groq API key is not loaded.")
        return

    client = AsyncOpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "user", "content": "Reply with OK"}
            ],
            max_tokens=10,
        )

        print("SUCCESS:", response.choices[0].message.content)

    except Exception as error:
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR DETAILS:", str(error))

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
