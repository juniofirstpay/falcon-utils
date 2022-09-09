import os
import falcon
import newrelic.agent
import traceback
from typing import Optional

DEFAULT_FILE_PATH = os.path.join(os.getcwd(), "./new-relic.ini")


def setup_new_relic(
    environment: str, app: "falcon.App", file_path: "Optional[str]" = None
):
    try:
        newrelic.agent.initialize(
            file_path or DEFAULT_FILE_PATH, environment=environment
        )
        return newrelic.agent.WSGIApplicationWrapper(app)
    except Exception as e:
        traceback.print_exc()
