import time
from typing import Dict, List

class RateLimiter:
    """In-memory sliding window rate limiter to prevent route abuse."""
    
    def __init__(self, limit: int = 5, period: float = 300.0):
        self.limit = limit          # Max requests allowed
        self.period = period        # Window period in seconds (e.g. 300.0s = 5 minutes)
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str) -> bool:
        """Checks if a client IP is within request thresholds, tracking the call time."""
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Keep only timestamps within the current window
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.period]
        
        if len(self.requests[client_ip]) >= self.limit:
            return False
            
        self.requests[client_ip].append(now)
        return True

# Rate limiter instance: maximum 5 authentication attempts per 5 minutes
auth_rate_limiter = RateLimiter(limit=5, period=300.0)
