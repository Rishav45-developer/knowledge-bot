
import json

from app.redis_client import redis_client


def get_cached_response(cache_key: str):
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data is None:
            return None

        return json.loads(cached_data)

    except Exception:
        # If Redis fails, continue without the cache.
        return None


def set_cached_response(
    cache_key: str,
    response: dict,
    ttl: int = 300
):
    try:
        redis_client.set(
            cache_key,
            json.dumps(response),
            ex=ttl
        )

    except Exception:
        # Caching should not break the chat service.
        pass
