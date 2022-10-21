from datetime import datetime
from falcon_utils.errors import UnAuthorizedSession


class SimpleAuthMiddleware(object):
    def __init__(self, config: dict, oauth_client=None):
        self.__config = config
        self.__oauth_client = oauth_client
        
        if self.__config.get("exempted_paths") is None:
            self.__config["exempted_paths"] = []

        if self.__config.get("clients") is None:
            self.__config["clients"] = {}

        if self.__config.get("api_keys") is None:
            self.__config["api_keys"] = []
        
        if self.__config.get("ip_whitelist") is None:
            self.__config["ip_whitelist"] = []

    def process_request(self, req: object, resp: object) -> object:
        self.request_initate_time = datetime.utcnow()
       
        token = None

        if req.path in self.__config.get("exempted_paths"):
            return

        if req.access_route[0] in self.__config.get("ip_whitelist"):
            return
        
        if req.headers.get("X-API-KEY") in self.__config.get("api_keys"):
            return

        client_id, client_secret = (
            req.headers.get("CLIENT-ID"),
            req.headers.get("CLIENT-SECRET"),
        )
        if (self.__config.get("clients") or {}).get(client_id) == client_secret and client_id is not None and client_secret is not None:
            return
        
        
        auth = req.headers.get("AUTHORIZATION", None)
        if auth and len(auth) > 0:
            auth_token_string = auth[7:]
            error, token = self.__oauth_client.introspection(
                None, None, auth_token_string, 'access_token')
            if not error:
                error, oauth_user = self.__oauth_client.get_user(auth_token=auth_token_string)
                if not error and oauth_user.get("username"):
                    setattr(req, 'user', oauth_user)
                    return
                
        raise UnAuthorizedSession()

    def process_response(self, req, resp, resource, params):
        pass
