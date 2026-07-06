import redis
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded singleton Redis connection reference
_redis_client: Optional[redis.Redis] = None
_redis_failed: bool = False

def get_redis_client() -> Optional[redis.Redis]:
    """Establishes and returns a Redis client session, catching connection failures gracefully."""
    global _redis_client, _redis_failed
    
    if not settings.REDIS_URL:
        return None

    if _redis_client is None and not _redis_failed:
        try:
            logger.info(f"Initializing connection to Redis at: {settings.REDIS_URL}")
            client = redis.Redis.from_url(
                settings.REDIS_URL,
                socket_connect_timeout=2.0,
                socket_timeout=2.0,
                decode_responses=True
            )
            client.ping()
            _redis_client = client
            logger.info("Distributed Redis caching connection established successfully.")
        except Exception as e:
            logger.warning(
                f"Redis connection failed. Caching and rate-limiting fallbacks will default "
                f"to in-memory mode. Error: {str(e)}"
            )
            _redis_failed = True
            _redis_client = None

    return _redis_client
