from datetime import datetime
from errors import UnAuthorizedSession


class SimpleAuthMiddleware(object):
    def __init__(self, config: dict):
        self.__config = config
        if self.__config.get("exempted_paths") is None:
            self.__config["exempted_paths"] = []

        if self.__config.get("clients") is None:
            self.__config["clients"] = {}

        if self.__config.get("api_keys") is None:
            self.__config["api_keys"] = []

    def process_request(self, req: object, resp: object) -> object:
        self.request_initate_time = datetime.utcnow()

        if req.path in self.__config.get("exempted_paths"):
            return

        if req.headers.get("X-API-KEY") in self.__config.get("api_keys"):
            return

        client_id, client_secret = (
            req.headers.get("CLIENT-ID"),
            req.headers.get("CLIENT-SECRET"),
        )
        if (self.__config.get("clients") or {}).get(client_id) == client_secret:
            return

        raise UnAuthorizedSession()

    def process_response(self, req, resp, resource, params):
        pass
