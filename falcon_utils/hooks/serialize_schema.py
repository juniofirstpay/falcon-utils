from typing import Type
from mongoengine import Document, QuerySet
from marshmallow import ValidationError
from marshmallow_objects import Model
from errors import DataSerializationError

class SerializeSchema(object):

    def __init__(self, schema: "Type[Model]", paginated=False):
        self.schema = schema
        self.paginated = paginated

    def __call__(self, req, resp, *args, **kwargs):
        try:
            data = resp.json
            if isinstance(data, list) or isinstance(data, QuerySet):
                resp.json = self.schema().dump(data, many=True)
                if self.paginated:
                    resp.json = {
                        'data': resp.json,
                        'count': resp.count,
                        'page': resp.page,
                        'page_size': resp.page_size
                    }
            elif issubclass(data.__class__, Document):
                resp.json = self.schema().dump(data)
            elif not isinstance(data, dict):
                resp.json = self.schema().dump(data)
            
        except ValidationError as err:
            raise DataSerializationError(err.messages)
