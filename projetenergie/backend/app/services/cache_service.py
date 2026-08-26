import json
from typing import Any
from app.db.redis_conn import redis_client

def get_cache(key: str) -> Any | None:
    """Get data from cache."""
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None

def set_cache(key: str, data: Any, ex: int = 3600):
    """Set data in cache with an expiration time."""
    redis_client.set(key, json.dumps(data), ex=ex)
