import time
import logging
from typing import Dict, List, Optional
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

class RateLimiter:
    """Hybrid rate limiter storing counts in Redis, falling back to local memory if offline."""
    
    def __init__(self, limit: int = 5, period: float = 300.0):
        self.limit = limit          # Max requests allowed
        self.period = period        # Window period in seconds (e.g. 300.0s = 5 minutes)
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str) -> bool:
        """Determines if a request from client_ip is within the rate limit."""
        client = get_redis_client()
        if client:
            try:
                key = f"rate_limit:{client_ip}"
                now = time.time()
                
                # Use Redis transaction pipeline to log call, prune and return count
                pipe = client.pipeline()
                pipe.lpush(key, now)
                pipe.ltrim(key, 0, self.limit * 2)  # Keep lists small to optimize space
                pipe.expire(key, int(self.period))
                pipe.lrange(key, 0, -1)
                results = pipe.execute()
                
                # Filter elements that fell outside the window
                timestamps = [float(t) for t in results[3]]
                valid_timestamps = [t for t in timestamps if now - t < self.period]
                
                if len(valid_timestamps) > self.limit:
                    return False
                return True
            except Exception as e:
                logger.warning(f"Redis rate limiting operation failed (falling back to memory): {str(e)}")

        # Fallback to Local In-Memory sliding window limiter
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Prune expired timestamps
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.period]
        
        # Garbage collect key if empty
        if not self.requests[client_ip]:
            self.requests.pop(client_ip, None)
            return True
            
        if len(self.requests[client_ip]) >= self.limit:
            return False
            
        self.requests[client_ip].append(now)
        return True

# Rate limiter instance: maximum 5 authentication attempts per 5 minutes
auth_rate_limiter = RateLimiter(limit=5, period=300.0)
