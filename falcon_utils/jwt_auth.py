import os
import requests
import datetime
from authlib.jose import jwt, JoseError
from functools import lru_cache, wraps

# TODO - update it appropriately
BASE_URL = os.environ.get("CORE_BASE_URL", "http://localhost:9000")
JWK_ENDPOINT = os.environ.get("JWK_ENDPOINT", "api/jwt/jwk")


def timed_lru_cache(seconds: int, maxsize: int = None):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = datetime.timedelta(seconds=seconds)
        func.expiration = datetime.datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


@timed_lru_cache(3600)
def fetch_jwk():
    url = f"{BASE_URL}/{JWK_ENDPOINT}"
    headers = {"X-Api-Version": "v1"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    return response.json()


def verify_token(token: str):
    try:
        jwk = fetch_jwk()
        if not jwk:
            return False, None

        decoded_token = jwt.decode(token, jwk)
        expires_at = decoded_token.get("exp")
        if not expires_at or expires_at < int(datetime.datetime.utcnow().timestamp()):
            return False, None

        return True, decoded_token
    except JoseError as err:
        return False, None
