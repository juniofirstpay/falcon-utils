import json
import falcon


class TestRoute:
    def on_get(self, req, resp):
        resp.text = json.dumps(["pong"])
        resp.status = falcon.code_to_http_status(200)