from datetime import datetime, timezone
from typing import Any, Optional

def success_response(data: Any, message: Optional[str] = None) -> dict:
    """Wraps positive endpoint outputs in a standardized JSON response envelope."""
    return {
        "success": True,
        "data": data,
        "error": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def error_response(message: str) -> dict:
    """Wraps routing or server exceptions in a standardized JSON response envelope."""
    return {
        "success": False,
        "data": None,
        "error": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
