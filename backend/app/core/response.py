from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

def success_response(data: Any = None) -> dict:
    return {
        "success": True,
        "data": data,
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }

def error_response(message: str) -> dict:
    return {
        "success": False,
        "data": None,
        "error": message,
        "timestamp": datetime.utcnow().isoformat()
    }
