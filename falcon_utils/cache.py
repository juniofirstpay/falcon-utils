from typing import Optional
from falcon_caching import Cache, middleware

@staticmethod
def generate_cache_key(req, method: str = None) -> str:
    """ Generate the cache key from the request using the path and the method """
    path = req.path
    if path.endswith('/'):
        path = path[:-1]

    if not method:
        method = req.method

    param_keys = list(req.params.keys())
    param_keys.sort()
    query_keys = []

    for key in param_keys:
        value = ",".join(req.get_param_as_list(key))
        query_keys.append(f"{key}:{value}")
    query_keys = ":".join(query_keys)

    return f'{path}:{method.upper()}:{query_keys}'

middleware.Middleware.generate_cache_key = generate_cache_key

def get_default_redis_cache(
    host: "str" = "localhost",
    port: "int" = 6379,
    db: "int" = 0,
    password: "Optional[str]" = None,
    redis_url: "Optional[str]" = None,
    key_prefix: "Optional[str]" = None,
):
    config={
        "CACHE_TYPE": "redis",
        "CACHE_EVICTION_STRATEGY": "time-based",
        "CACHE_KEY_PREFIX": key_prefix,
    }
    if redis_url:
        config.update({ 'CACHE_REDIS_URL': redis_url })
    else:
        config.update({ 
            "CACHE_REDIS_HOST": host,
            "CACHE_REDIS_PORT": port,
            "CACHE_REDIS_PASSWORD": password,
            "CACHE_REDIS_DB": db
        })
    return Cache(config=config)