import inspect
import functools
from typing import Optional
from falcon_caching.middleware import _DECORABLE_METHOD_NAME
from falcon_caching import Cache, middleware
# from falcon_caching.options import CacheEvictionStrategy, HttpMethods
# from falcon import HTTP_200
# import logging

# FALCONVERSION_MAIN = 3


@staticmethod
def cached(timeout: int):
    """ This is the decorator used to decorate a resource class or the requested
    method of the resource class
    """
    def wrap1(class_or_method, *args):
        # is this about decorating a class or a given method?
        if inspect.isclass(class_or_method):
            # get all methods of the class that needs to be decorated (eg start with "on_"):
            for attr in dir(class_or_method):
                if callable(getattr(class_or_method, attr)) and _DECORABLE_METHOD_NAME.match(attr):
                    setattr(class_or_method, attr, wrap1(getattr(class_or_method, attr)))

            return class_or_method
        else:  # this is to decorate the individual method
            class_or_method.to_be_cached = True

            def cache_wrap(cls, req, resp, *args, **kwargs):
                print("WRAPPED_CACHE_FUNCTION_CALLED")
                class_or_method(cls, req, resp, *args, **kwargs)
                req.context.cache = True
                req.context.cache_timeout = timeout

            return cache_wrap

    # this is the name which will check for if the decorator was registered with the register()
    # function, as this decorator is not the topmost one
    wrap1._decorator_name = 'cache'  # type: ignore

    return wrap1


Cache.cached = cached

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

    cache_key = f'{path}:{method.upper()}:{query_keys}'
    jwt_exists = req.headers.get("X-JWT")
    if jwt_exists:
        cache_key = f'{cache_key}:{"jwt"}'

    return cache_key


# def process_resource(self, req, resp, resource, params):
#     """ Determine if the given request is marked for caching and if yes,
#     then look it up in the cache and if found, then return the cached value
#     """

#     # Step 1: for 'rest-based' and 'rest&time-based' eviction strategies the
#     # POST/PATCH/PUT/DELETE calls are never cached, they should never be
#     # loaded from cache as they must always execute,
#     # so for those we don't need to try to search the cache
#     if self.cache_config['CACHE_EVICTION_STRATEGY'] in [CacheEvictionStrategy.rest_based,
#                                                         CacheEvictionStrategy.rest_and_time_based] \
#         and req.method.upper() in [HttpMethods.POST,
#                                     HttpMethods.PATCH,
#                                     HttpMethods.PUT,
#                                     HttpMethods.DELETE]:
#         return

#     # Step 2: determine whether the given responder has caching setup
#     # and if not then short-circuit to save on the lookup of request in the cache
#     # as anyhow this request was not marked to be cached

#     # find out which responder ("on_..." method) is going to be used to process this request
#     responder = None
#     for _method in dir(resource):
#         if _DECORABLE_METHOD_NAME.match(_method) and _method[3:].upper() == req.method.upper():
#             responder = _method
#             break

#     if responder:
#         # get the name of the responder wrapper, which for cached objects is 'cache_wrap'
#         # see the "Cache.cache" decorator in cache.py
#         responder_wrapper_name = getattr(getattr(resource, responder), '__name__')


#         # is the given method (or its class) decorated by the cache_wrap being the topmost decorator?
#         if responder == responder_wrapper_name and responder in getattr(resource, 'cached_methods', []):
#             logging.debug("This endpoint is decorated using cached methods dict")
#         elif responder_wrapper_name == 'cache_wrap':
#             logging.debug(" This endpoint is decorated by 'cache' being the topmost decorator.")
#         else:
#             # 'cache_wrap' is not the topmost decorator - let's check whether 'cache' is
#             # any of the other decorator on this method (not the topmost):
#             # this requires the use of @register(decor1, decor2) as the decorator
#             if hasattr(getattr(resource, responder), '_decorators') and \
#                     'cache' in [d._decorator_name for d in getattr(resource, responder)._decorators
#                                 if hasattr(d, '_decorator_name')]:
#                 logging.debug(" This endpoint is decorated by 'cache', but it is NOT the topmost decorator.")
#             else:
#                 # no cache was requested on this responder as no decorator at all
#                 logging.debug(" No 'cache' was requested for this endpoint.")
#                 return

#     # Step 3: look up the record in the cache
#     key = self.generate_cache_key(req)
#     data = self.cache.get(key)

#     if data:
#         # if the CACHE_CONTENT_TYPE_JSON_ONLY = True, then we are NOT
#         # caching the response's Content-Type, only its body
#         if self.cache_config['CACHE_CONTENT_TYPE_JSON_ONLY']:
#             if FALCONVERSION_MAIN < 3:
#                 resp.body = self.deserialize(data)
#             else:
#                 resp.text = self.deserialize(data)
#         else:
#             if FALCONVERSION_MAIN < 3:
#                 resp.content_type, resp.body = self.deserialize(data)
#             else:
#                 resp.content_type, resp.text = self.deserialize(data)
#         resp.status = HTTP_200
#         req.context.cached = True

#         # Short-circuit any further processing to skip any remaining
#         # 'process_request' and 'process_resource' methods, as well as
#         # the 'responder' method that the request would have been routed to.
#         # However, any 'process_response' middleware methods will still be called.
#         resp.complete = True


middleware.Middleware.generate_cache_key = generate_cache_key
# middleware.Middleware.process_resource = process_resource

def get_default_redis_cache(
    host: "str" = "localhost",
    port: "int" = 6379,
    db: "int" = 0,
    password: "Optional[str]" = None,
    key_prefix: "Optional[str]" = None,
    redis_url: "Optional[str]" = None,
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