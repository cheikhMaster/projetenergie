import json
from typing import Any, Optional
from app.db.redis_conn import redis_client


def get_cache(key: str) -> Optional[Any]:
    """Récupère une valeur du cache. Retourne None si absente ou expirée."""
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None


def set_cache(key: str, data: Any, ex: int = 3600) -> None:
    """Stocke une valeur dans le cache avec une expiration (secondes)."""
    redis_client.set(key, json.dumps(data), ex=ex)


def delete_cache_pattern(pattern: str) -> int:
    """
    Supprime toutes les clés correspondant à un pattern Redis (ex: 'centrales:*').
    Retourne le nombre de clés supprimées. Utilisé pour invalider le cache
    après un import Excel (ex: delete_cache_pattern('centrales:*')).
    """
    keys = redis_client.keys(pattern)
    if keys:
        return redis_client.delete(*keys)
    return 0
