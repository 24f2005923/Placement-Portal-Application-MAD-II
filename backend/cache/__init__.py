# Cache package — exposes the shared cache instance used across the application.
from cache.redis_cache import RedisCache

# Single shared cache instance.
# Routes and tasks import this object directly:
#   from cache import cache
cache = RedisCache()
