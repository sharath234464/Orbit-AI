from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, messages, model: str, temperature: float, max_output_tokens: int) -> dict:
        raise NotImplementedError

    async def close(self):
        return None
