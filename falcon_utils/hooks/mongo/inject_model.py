import stringcase
from typing import Type, Callable
from mongoengine import Document

class inject_model(object):
    
    def __init__(self, model: "Type[Document]", key: "str", callable: "Callable", alias: "str"=None):
        self.model = model
        self.key = key
        self.callable = callable
        self.alias = None
        
    def __call__(self, req, resp, resource, params):
        value = self.callable.__call__(req, resp, resource, params)
        if value is not None:
            obj = self.model.objects.filter({self.key: value}).first()
            setattr(req, self.alias or stringcase.snakecase(self.model.__name__), obj)
        
        