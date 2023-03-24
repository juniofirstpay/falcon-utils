from enum import Enum
import json
import requests
import datetime
from jwcrypto.jwt import JWT
from jwcrypto.common import JWException
from jwcrypto.jwk import JWKSet
from functools import lru_cache, wraps


def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = datetime.timedelta(seconds=seconds)
        func.expiration = datetime.datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.datetime.utcnow() + func.lifetime

            result = func(*args, **kwargs)
            return result
        return wrapped_func
    return wrapper_cache


class JWTVerifyService:
    def __init__(self, url: str) -> None:
        self.service_url = url

    @timed_lru_cache(3600)
    def fetch_jwk(self):
        headers = {"X-Api-Version": "v1"}
        response = requests.get(self.service_url, headers=headers)
        if response.status_code != 200:
            return None

        return response.json()

    def verify(self, token: str):
        try:
            jwk_dict = self.fetch_jwk()
            if not jwk_dict:
                return False, None

            jwk_set = JWKSet.from_json(json.dumps(jwk_dict))
            decoded_token = JWT(key=jwk_set, jwt=token)
            
            claims = json.loads(decoded_token.claims)
            expires_at = claims.get("exp")
            if not expires_at or expires_at < int(
                datetime.datetime.utcnow().timestamp()
            ):
                return False, None

            return True, claims
        except JWException as err:
            return False, None


class AuthorizationScheme(Enum):
    JWT = "jwt"
    EXEMPTED_PATH = "exempted_path"
    IP_WHITELIST = "ip_whitelist"
    API_KEY = "api_key"
    CLIENT_SECRET = "client_secret"
    ACCESS_TOKEN = "access_token"


class AccessLevel(Enum):
    SELF = 'self'
    DEPENDANT = 'dependant'
    SELF_AND_DEPENDANT = 'self_and_dependant'