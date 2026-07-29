import functools
import json
import logging
from flask import request, Response

logger = logging.getLogger(__name__)

def cache_response(key_fn, ttl=300):
    """
    Flask route decorator that caches the response as JSON using Redis.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            from cache import cache

            cache_key = key_fn()
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return Response(
                    json.dumps(cached_value, default=str),
                    status=200,
                    mimetype='application/json'
                )

            logger.debug(f"Cache MISS: {cache_key}")
            response = view_func(*args, **kwargs)

            status_code = response[1] if isinstance(response, tuple) else 200
            if status_code == 200:
                try:
                    resp_obj = response[0] if isinstance(response, tuple) else response
                    data = json.loads(resp_obj.get_data(as_text=True))
                    cache.set(cache_key, data, ttl=ttl)
                except Exception as exc:
                    logger.warning(f"Could not cache response for {cache_key}: {exc}")

            return response

        return wrapper
    return decorator

def page_key():
    """Returns the page query string argument."""
    return request.args.get('page', '1')

def search_key():
    """Returns the cleaned search query string argument."""
    return request.args.get('search', '').strip().lower()

def status_key():
    """Returns the status query string argument."""
    return request.args.get('status', '').strip().lower()
