import falcon
from datetime import datetime
from falcon_utils.errors import UnAuthorizedSession

from falcon_utils.auth import AuthorizationScheme, JWTVerifyService


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
            req.context["authorization_scheme"] = AuthorizationScheme.EXEMPTED_PATH
            return

        if req.access_route[0] in self.__config.get("ip_whitelist"):
            req.context["authorization_scheme"] = AuthorizationScheme.IP_WHITELIST
            return

        if req.headers.get("X-API-KEY") in self.__config.get("api_keys"):
            req.context["authorization_scheme"] = AuthorizationScheme.API_KEY
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
            req.context["authorization_scheme"] = AuthorizationScheme.CLIENT_SECRET
            return

        jwt_auth = req.headers.get("X-JWT", None)
        if jwt_auth:
            service_url = self.__config["jwk_service_url"]
            verified, token = JWTVerifyService(service_url).verify(jwt_auth)
            if not verified:
                raise UnAuthorizedSession()
            
            req.context["authorization_scheme"] = AuthorizationScheme.JWT
            req.context["authorization_payload"] = token
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
                    req.context["authorization_scheme"] = AuthorizationScheme.ACCESS_TOKEN
                    return

        raise UnAuthorizedSession()

    def process_resource(self, req, resp, resource, params):
        """
        Validate whethter the resource has specified any authorization schemes
        to be validated against and was that authorization scheme added by `process_request`. 
        In case no authorization scheme is specified, endpoint is assumed to be 
        publicly available.
        """
        authorization_schemes = getattr(resource, "authorization_schemes", [])
        if len(authorization_schemes) == 0:
            return

        request_authorization_scheme = req.context.get("authorization_scheme", None)
        if (
            request_authorization_scheme is None
            or request_authorization_scheme not in authorization_schemes
        ):
            raise UnAuthorizedSession()

    def process_response(self, req, resp, resource, params):
        pass
