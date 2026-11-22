from enum import Enum

class RequestStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
