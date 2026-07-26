"""
decorators.py — Flask route caching decorator
──────────────────────────────────────────────
Usage in a route file:

    from cache import cache
    from cache.decorators import cache_response

    @student_bp.route('/drives', methods=['GET'])
    @student_required
    @cache_response(lambda: 'student:drives', ttl=120)
    def list_open_drives():
        ...

The decorator:
  1. Generates a cache key by calling *key_fn()*.
  2. Returns the cached JSON response if found (cache HIT).
  3. Otherwise calls the real route function, stores the result,
     and returns it (cache MISS).

Key builder helpers at the bottom of this file make it easy to
build parameterised keys that include query-string values.
"""

import functools
import json
import logging
from flask import request, Response

logger = logging.getLogger(__name__)


def cache_response(key_fn, ttl: int = 300):
    """
    Decorator factory that caches a Flask route's JSON response.

    Args:
        key_fn: A zero-argument callable that returns the cache key
                string.  It is called *inside* the request context
                so you can safely call request.args inside it.
        ttl:    Cache lifetime in seconds (default 5 minutes).

    Example:
        @cache_response(lambda: f'admin:students:{request.args.get("page", 1)}', ttl=180)
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            # Import here to avoid circular imports at module load time.
            from cache import cache

            cache_key = key_fn()

            # ── Cache HIT ─────────────────────────────────────────
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug('Cache HIT: %s', cache_key)
                # Re-wrap the dict as a proper Flask JSON response.
                return Response(
                    json.dumps(cached_value, default=str),
                    status=200,
                    mimetype='application/json'
                )

            # ── Cache MISS — call the real route ──────────────────
            logger.debug('Cache MISS: %s', cache_key)
            response = view_func(*args, **kwargs)

            # Only cache successful (2xx) responses.
            status_code = response[1] if isinstance(response, tuple) else 200
            if status_code == 200:
                try:
                    # response may be (jsonify_obj, 200) or just jsonify_obj
                    resp_obj = response[0] if isinstance(response, tuple) else response
                    data = json.loads(resp_obj.get_data(as_text=True))
                    cache.set(cache_key, data, ttl=ttl)
                except Exception as exc:
                    # Caching is best-effort; never break the route.
                    logger.warning('Could not cache response for %s: %s', cache_key, exc)

            return response

        return wrapper
    return decorator


# ── Key builder helpers ───────────────────────────────────────────
# These are small functions you can use inside key_fn lambdas to
# build consistent, descriptive cache keys.

def page_key():
    """Returns the current page number from query string (default 1)."""
    return request.args.get('page', '1')

def search_key():
    """Returns the search term from query string (default empty string)."""
    return request.args.get('search', '').strip().lower()

def status_key():
    """Returns the status filter from query string."""
    return request.args.get('status', '').strip().lower()
