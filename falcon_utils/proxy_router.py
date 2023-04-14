import functools
from typing import Callable, Optional


class ProxyRouter:
    def __init__(
        self,
        header_value: "str",
        service_header_key: "str",
        request_modifier: "Optional[Callable]" = lambda *args, **kwargs: None,
        response_modifier: "Optional[Callable]" = lambda *args, **kwargs: None,
    ):
        self.__proxy_header_value = header_value
        self.__service_header_key = service_header_key
        self.__proxy_request_modifier = request_modifier
        self.__proxy_response_modifier = response_modifier

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper_func(
            obj, req: "falcon.Request", resp: "falcon.Response", *args, **kwargs
        ):
            if req.headers.get(self.__service_header_key) == self.__proxy_header_value:
                req.context["is_proxy"] = True

                self.__proxy_request_modifier(req)
                func(obj, req, resp, *args, **kwargs)
                self.__proxy_response_modifier(req, resp)

                return

            return func(obj, req, resp, *args, **kwargs)

        return wrapper_func
