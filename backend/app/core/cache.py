import json
import logging
from typing import Any, Optional
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

# Core in-memory storage fallback when Redis is absent
_memory_cache = {}

def get_cache(key: str) -> Optional[Any]:
    """Retrieves a cached JSON payload. Returns None if Redis is offline or disabled."""
    client = get_redis_client()
    if client:
        try:
            val = client.get(key)
            if val:
                return json.loads(val)
        except Exception as e:
            logger.warning(f"Redis Cache GET failure: {str(e)}")
            
    return None

def set_cache(key: str, value: Any, expire_seconds: int = 300) -> None:
    """Stores a serialized JSON value in the cache with a specific expiration TTL."""
    client = get_redis_client()
    if client:
        try:
            client.set(key, json.dumps(value), ex=expire_seconds)
            return
        except Exception as e:
            logger.warning(f"Redis Cache SET failure: {str(e)}")

def delete_cache(key: str) -> None:
    """Evicts a key from the cache."""
    client = get_redis_client()
    if client:
        try:
            client.delete(key)
            return
        except Exception as e:
            logger.warning(f"Redis Cache DELETE failure: {str(e)}")

def invalidate_disaster_cache() -> None:
    """Evicts all cached disaster lists to ensure data consistency after inserts."""
    client = get_redis_client()
    if client:
        try:
            # Locate all lists cached under versioned patterns
            keys = client.keys("disasters_list:*")
            if keys:
                client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} Redis cache keys for disasters list.")
            return
        except Exception as e:
            logger.warning(f"Redis Cache invalidation failure: {str(e)}")

