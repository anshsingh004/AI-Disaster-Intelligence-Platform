import redis
import time
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded singleton Redis connection references
_redis_client: Optional[redis.Redis] = None
_last_connect_attempt: float = 0.0
_connect_cooldown: float = 30.0  # Cooldown period in seconds before retrying connection

def get_redis_client() -> Optional[redis.Redis]:
    """Establishes and returns a Redis client session, retrying connection after cooldown if offline."""
    global _redis_client, _last_connect_attempt
    
    if not settings.REDIS_URL:
        return None

    if _redis_client is not None:
        return _redis_client

    now = time.time()
    # If connection previously failed, wait for the cooldown interval to avoid blocking client requests
    if now - _last_connect_attempt < _connect_cooldown:
        return None

    _last_connect_attempt = now
    try:
        logger.info(f"Initializing connection to Redis at: {settings.REDIS_URL}")
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=1.5,  # Slightly shorter connect timeout for faster fallbacks
            socket_timeout=1.5,
            decode_responses=True
        )
        client.ping()
        _redis_client = client
        logger.info("Distributed Redis caching connection established successfully.")
    except Exception as e:
        logger.warning(
            f"Redis connection failed (retry cooldown active). Falling back to in-memory utilities. "
            f"Error: {str(e)}"
        )
        _redis_client = None

    return _redis_client
