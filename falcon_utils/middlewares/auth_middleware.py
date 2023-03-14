import falcon
from datetime import datetime
from falcon_utils.errors import UnAuthorizedSession

from falcon_utils.jwt_auth import JWTVerifyService


class SimpleAuthMiddleware(object):
    def __init__(self, config: dict, oauth_client=None):
        self.__config = config
        self.__oauth_client = oauth_client

        self.__config["exempted_paths"] = self.__config.get("exempted_paths", [])
        self.__config["clients"] = self.__config.get("clients", {})
        self.__config["api_keys"] = self.__config.get("api_keys", [])
        self.__config["ip_whitelist"] = self.__config.get("ip_whitelist", [])
        self.__config["jwk_service_url"] = self.__config.get(
            "jwk_service_url", "http://localhost:9000/api/jwt/jwk"
        )

    def process_request(self, req: "falcon.Request", resp: "falcon.Response") -> object:
        self.request_initate_time = datetime.utcnow()

        if req.method == "OPTIONS":
            resp.status = falcon.HTTP_200
            return

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
        if (
            (self.__config.get("clients") or {}).get(client_id) == client_secret
            and client_id is not None
            and client_secret is not None
        ):
            return

        jwt_auth = req.headers.get("JWT", None)
        if jwt_auth:
            service_url = self.__config["jwk_service_url"]
            verified, token = JWTVerifyService(service_url).verify(jwt_auth)
            if not verified:
                raise UnAuthorizedSession()

            setattr(req, "authorisation", token)
            return

        auth = req.headers.get("AUTHORIZATION", None)
        if auth and len(auth) > 0:
            auth_token_string = auth[7:]
            error, token = self.__oauth_client.introspection(
                None, None, auth_token_string, "access_token"
            )
            if not error:
                error, oauth_user = self.__oauth_client.get_user(
                    auth_token=auth_token_string
                )
                if not error and oauth_user.get("username"):
                    setattr(req, "user", oauth_user)
                    return

        raise UnAuthorizedSession()

    def process_response(self, req, resp, resource, params):
        pass
