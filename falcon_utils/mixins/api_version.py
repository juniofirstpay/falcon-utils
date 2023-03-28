from typing import Callable, Dict, Optional, Tuple
import falcon

from falcon_utils.errors import InvalidApiVersionScheme


class ApiVersioningScheme(object):
    def on_get(self, req: "falcon.Request", resp: "falcon.Request", *args, **kwargs):
        api_version: "Optional[str]" = req.headers.get("X-API-VERSION")
        if not api_version:
            self.get(req, resp, *args, **kwargs)
            return

        route_handler: Callable[
            [falcon.Request, falcon.Response, Tuple, Dict], None
        ] = getattr(self, f"on_get_{api_version}", None)
        if not route_handler:
            raise InvalidApiVersionScheme()

        route_handler(req, resp, *args, **kwargs)

    def on_post(self, req: "falcon.Request", resp: "falcon.Request", *args, **kwargs):
        api_version: "Optional[str]" = req.headers.get("X-API-VERSION")
        if not api_version:
            self.post(req, resp, *args, **kwargs)
            return

        route_handler: Callable[
            [falcon.Request, falcon.Response, Tuple, Dict], None
        ] = getattr(self, f"on_post_{api_version}", None)
        if not route_handler:
            raise InvalidApiVersionScheme()

        route_handler(req, resp, *args, **kwargs)
