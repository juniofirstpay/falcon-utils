from typing import Type
from marshmallow import ValidationError
from marshmallow_objects import Model
from errors import SchemaValidationError


class ValidateSchema(object):

    def __init__(self, schema: "Type[Model]", list=False):
        self.schema= schema
        self.list = list

    def __call__(self, req, resp, resource, params):
        try:
            data = req.json
            if self.list:
                req.context['data'] = self.schema(many=True).load(data)
            else:
                req.context['data'] = self.schema(**data)
        except ValidationError as err:
            raise SchemaValidationError(err.messages)


class ValidateParams(object):

    def __init__(self, schema: Type[Model]):
        self.schema = schema

    def __call__(self, req, resp, resource, params):
        try:
            req.context['params'] = self.schema(**params)
        except ValidationError as err:
            SchemaValidationError(err.messages)