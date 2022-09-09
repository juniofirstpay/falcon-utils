import requests
from typing import Optional, Type, Tuple, Union, Dict
from marshmallow_objects import Schema

def process_result_with_code(result: requests.Response,
                             req_log_obj=None,
                             schema: Optional[Type[Schema]] = None) -> Tuple[int, Union[Dict, str]]:
    response = {}
    if result.status_code == 200:
        if schema is not None:
            response = schema(**result.json())
        else:
            response = result.json()
    elif result.status_code >= 400:
        try:
            response = result.json()
        except Exception as e:
            response = {"error": result.text}

    return result.status_code, response