import falcon
from typing import Any, Callable, Dict, Tuple

from falcon_utils.auth import AccessLevel, AuthorizationScheme
from falcon_utils.errors import UnAuthorizedSession


class AuthorizePayload:
    def __init__(
        self,
        callable: Callable[
            [Tuple["falcon.Request", "falcon.Response", Any, Dict]], str
        ],
        level: AccessLevel,
    ) -> None:
        self.callable = callable
        self.level = level

    def __call__(
        self, req: "falcon.Request", resp: "falcon.Response", resource, params: "Dict"
    ) -> None:
        authorization_scheme = req.context.get("authorization_scheme")
        if authorization_scheme != AuthorizationScheme.JWT:
            return
        
        authorization_payload = req.context.get("authorization_payload")
        if authorization_payload == None:
            raise UnAuthorizedSession()

        value = self.callable((req, resp, resource, params))
        if value == None:
            raise UnAuthorizedSession()

        profiles = authorization_payload.get("profiles")
        person_ids = {
            AccessLevel.SELF: profiles.get("self", []),
            AccessLevel.DEPENDANT: profiles.get("dependants", []),
            AccessLevel.SELF_AND_DEPENDANT: profiles.get("self", [])
            + profiles.get("dependants", []),
        }

        if value in person_ids[self.level]:
            return

        raise UnAuthorizedSession()
