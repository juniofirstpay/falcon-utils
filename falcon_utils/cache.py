from typing import Optional
from falcon_caching import Cache


def get_default_redis_cache(
    host: "str" = "localhost",
    port: "int" = 6379,
    db: "int" = 0,
    password: "Optional[str]" = None,
    key_prefix: "Optional[str]" = None,
):
    return Cache(
        config={
            "CACHE_TYPE": "redis",
            "CACHE_EVICTION_STRATEGY": "time-based",
            "CACHE_REDIS_HOST": host,
            "CACHE_REDIS_PORT": port,
            "CACHE_REDIS_PASSWORD": password,
            "CACHE_REDIS_DB": db,
            "CACHE_KEY_PREFIX": key_prefix,
        }
    )