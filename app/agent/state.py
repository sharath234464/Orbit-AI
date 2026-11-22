from typing import TypedDict, Any

class RoutingState(TypedDict, total=False):
    messages: list[Any]
    requested_model: str
    task_type: str
    provider_name: str
    model_name: str
    routing_reason: str
