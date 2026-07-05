import time
from typing import Dict, Any, Tuple, Optional

class InferenceCache:
    """In-memory prediction cache matching inputs to pre-computed outputs to minimize latency."""

    def __init__(self, ttl_seconds: float = 300.0):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Fetches a cached response if valid, otherwise discards expired entries."""
        if key in self.cache:
            timestamp, val = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return val
            # Garbage collect expired cache keys
            self.cache.pop(key, None)
        return None

    def set(self, key: str, value: Any) -> None:
        """Saves a prediction response with current timestamp."""
        self.cache[key] = (time.time(), value)

    def clear(self) -> None:
        """Invalidates all cache entries."""
        self.cache.clear()

# Shared inference caching layer (expires in 5 minutes)
prediction_cache = InferenceCache(ttl_seconds=300.0)
