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
            # Garbage collect expired cache keys on-demand
            self.cache.pop(key, None)
        return None

    def set(self, key: str, value: Any) -> None:
        """Saves a prediction response with current timestamp, sweeping expired keys if size grows."""
        # Bounded cache pruning to prevent memory growth leaks in long-running processes
        if len(self.cache) > 1000:
            now = time.time()
            expired_keys = [k for k, (t, _) in self.cache.items() if now - t >= self.ttl]
            for k in expired_keys:
                self.cache.pop(k, None)
                
        self.cache[key] = (time.time(), value)

    def clear(self) -> None:
        """Invalidates all cache entries."""
        self.cache.clear()

# Shared inference caching layer (expires in 5 minutes)
prediction_cache = InferenceCache(ttl_seconds=300.0)
