from typing import Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    conversation_id: str | None = None
    model: str = "auto"
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_output_tokens: int = Field(default=1000, ge=1, le=16000)

class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

class ChatResponse(BaseModel):
    request_id: str
    conversation_id: str
    model: str
    provider: str
    content: str
    usage: Usage
    latency_ms: float
    task_type: str
    routing_reason: str
