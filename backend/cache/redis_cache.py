"""
redis_cache.py — Low-level Redis cache helper
─────────────────────────────────────────────
Provides a simple get / set / delete interface on top of the Redis
client.  All values are stored as JSON strings so any Python dict or
list can be cached directly.

Design notes:
  • If Redis is not running, every operation is silently skipped so
    the application continues to work (just without caching).
  • The TTL (time-to-live) controls how long a cached value lives
    before Redis automatically removes it.
"""

import json
import logging
import os

try:
    import redis
    HAS_REDIS = True
except ImportError:
    redis = None
    HAS_REDIS = False

logger = logging.getLogger(__name__)


class RedisCache:
    """Thin wrapper around redis.Redis for JSON-serialised caching."""

    def __init__(self):
        # Check if the python redis package is installed.
        if not HAS_REDIS:
            self._client = None
            self._available = False
            logger.warning(
                'Redis module is not installed ("redis" package missing). Caching is disabled — '
                'all routes will work normally, just without caching.'
            )
            return

        # Read the Redis URL from the environment (or fall back to localhost).
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self._client = redis.Redis.from_url(
                redis_url,
                decode_responses=True,   # automatically decode bytes → str
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Ping once at startup to detect connection issues early.
            self._client.ping()
            self._available = True
            logger.info('Redis cache connected: %s', redis_url)
        except Exception as exc:
            self._client = None
            self._available = False
            logger.warning(
                'Redis is not available (%s). Caching is disabled — '
                'all routes will work normally, just without caching.', exc
            )


    # ── Public API ────────────────────────────────────────────────

    def get(self, key: str):
        """
        Retrieve a cached value by key.

        Returns the deserialised Python object, or None if the key
        does not exist or Redis is unavailable.
        """
        if not self._available:
            return None
        try:
            raw = self._client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.error('Cache GET error for key %s: %s', key, exc)
            return None

    def set(self, key: str, value, ttl: int = 300):
        """
        Store *value* under *key* with an expiry of *ttl* seconds.

        Args:
            key:   Cache key string (e.g. 'admin:stats').
            value: Any JSON-serialisable Python object.
            ttl:   Seconds until the entry expires (default 5 minutes).
        """
        if not self._available:
            return
        try:
            serialised = json.dumps(value, default=str)
            self._client.setex(key, ttl, serialised)
        except Exception as exc:
            logger.error('Cache SET error for key %s: %s', key, exc)

    def delete(self, key: str):
        """Remove a single cache entry by its exact key."""
        if not self._available:
            return
        try:
            self._client.delete(key)
            logger.debug('Cache invalidated: %s', key)
        except Exception as exc:
            logger.error('Cache DELETE error for key %s: %s', key, exc)

    def delete_pattern(self, pattern: str):
        """
        Remove all cache keys that match a glob-style pattern.

        Example: delete_pattern('admin:students:*') removes all
        paginated student list results at once.
        """
        if not self._available:
            return
        try:
            # SCAN is safer than KEYS in production (non-blocking).
            matching_keys = list(self._client.scan_iter(pattern))
            if matching_keys:
                self._client.delete(*matching_keys)
                logger.debug('Cache invalidated %d key(s) matching %s',
                             len(matching_keys), pattern)
        except Exception as exc:
            logger.error('Cache DELETE_PATTERN error for %s: %s', pattern, exc)

    def flush_all(self):
        """Clear the entire cache database (use sparingly — dev/test only)."""
        if not self._available:
            return
        try:
            self._client.flushdb()
            logger.warning('Cache flushed (entire database cleared).')
        except Exception as exc:
            logger.error('Cache FLUSH error: %s', exc)

    @property
    def is_available(self) -> bool:
        """True if Redis is reachable, False otherwise."""
        return self._available
