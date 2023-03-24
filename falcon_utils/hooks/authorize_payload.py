import falcon
from typing import Callable, Dict

from falcon_utils.auth import AccessLevel
from falcon_utils.errors import UnAuthorizedSession


class AuthorizePayload:
    def __init__(self, callable: Callable[[falcon.Request], str], level: AccessLevel) -> None:
        self.callable = callable
        self.level = level

    def __call__(self, req: falcon.Request, resp: falcon.Response, resource, params: Dict) -> None:
        authorization_payload = req.context.get("authorization_payload")
        if authorization_payload == None:
            return
        
        value = self.callable(req)
        if value == None:
            return
        
        profiles = authorization_payload.get("profiles")
        person_ids = {
            AccessLevel.SELF: profiles.get("self", []),
            AccessLevel.DEPENDANT: profiles.get("dependants", []),
            AccessLevel.SELF_AND_DEPENDANT: profiles.get("self", []) + profiles.get("dependants", [])
        }

        if value in person_ids[self.level]:
            return
        
        raise UnAuthorizedSession()