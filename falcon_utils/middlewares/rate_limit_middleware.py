import enum
import functools
from typing import List, Dict
from limits import storage, strategies, parse
from falcon_utils.errors import RateLimitError

class RateLimitingMiddleware:
    
    class Type(enum.Enum):
        FIXED_WINDOW = 1
        ELASTIC_WINDOW = 2
        MOVING_WINDOW = 3
    
    def __init__(self, config: "Dict"):
        self.__limiters = {}
        self.__config = config
        self.__storage = storage.RedisStorage(f"redis://{self.__config['username']}:{self.__config['password']}@{self.__config['host']}:{self.__config['port']}")
        if self.__config["type"] == self.Type.FIXED_WINDOW:
            self.__strategy = strategies.FixedWindowRateLimiter(self.__storage)
        elif self.__config["type"] == self.Type.ELASTIC_WINDOW:
            self.__strategy = strategies.FixedWindowElasticExpiryRateLimiter(self.__storage)
        elif self.__config["type"] == self.Type.MOVING_WINDOW:
            self.__strategy = strategies.MovingWindowRateLimiter(self.__storage)
        
    def process_resource(self, req, resp, resource, params):
        limiters = self.__limiters.get(f"{resource.__class__.__name__}:on_{req.method.lower()}")
        if limiters is not None and isinstance(limiters, list):
            blocking_limit_item = next(filter(lambda limit_item: self.__strategy.hit(limit_item, req.path, req.method) == False, limiters), None)
            if blocking_limit_item is not None:
                raise RateLimitError()
    
    def apply_limits(self, limiters: "List[str]"):
        
        def hook_func(func):
            self.__limiters[f"{func.__module__}:{func.__name__}"] = list(map(lambda x: parse(x), limiters))
            return func
            
        return hook_func
    
    