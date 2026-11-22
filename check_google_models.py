
from google import genai
from app.core.config import get_settings

settings = get_settings()

if not settings.google_api_key:
    print("Google API key was not loaded.")
else:
    client = genai.Client(api_key=settings.google_api_key)

    try:
        for model in client.models.list():
            actions = getattr(model, "supported_actions", None)
            if not actions or "generateContent" in actions:
                print(model.name, "|", actions)
    except Exception as error:
        print(type(error).__name__, str(error))
