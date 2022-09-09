from marshmallow_objects import ValidationError
from falcon_utils.errors import SchemaValidationError


class MapQuery(object):

    def __init__(self, schema, list_fields=[]):
        self.schema = schema
        self.list_fields = list_fields

    def __call__(self, req, resp, resource, params):
        try:
            for field in self.list_fields:
                req.params[field] = req.get_param_as_list(field)
            setattr(req.context, 'data', self.schema(**req.params))
        except ValidationError as err:
            raise SchemaValidationError(err.messages)
