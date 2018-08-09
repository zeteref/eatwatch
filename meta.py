import json
from datetime import datetime
from marshmallow import Schema, fields, post_load

__all__ = ['JsonObject', 'fields']

def _fix_for_marshmallow_datetime_serialization(_fields):
    # TODO: send pull request or wait for fix in fields.py:911
    _date_fields = [x for (_, x) in _fields.items() if isinstance(x, fields.DateTime)]
    for _date_field in _date_fields:
        if hasattr(_date_field, 'dateformat'):
            def _strftime(value, localtime):
                return value.strftime(_date_field.dateformat)

            fields.DateTime.DATEFORMAT_SERIALIZATION_FUNCS[_date_field.dateformat] = _strftime


class Meta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        _fix_for_marshmallow_datetime_serialization(namespace)
        schema_fields = [(k,v) for (k,v) in namespace.items() if isinstance(v, fields.Field)]
        namespace = dict([(k,v) for (k,v) in namespace.items() if not isinstance(v, fields.Field)])

        new_cls = super(Meta, mcs).__new__(mcs, name, bases, namespace, **kwargs)

        def __init__(self, **data):
            for k,v in data.items():
                setattr(self, k, v)

        setattr(new_cls, '__init__', __init__)

        _Schema = type(name+'Schema', (Schema,), dict(schema_fields))


        def loads(data):
            dic, err = _Schema().loads(data)
            return new_cls(**dic)
        

        # since we will be *only* marshalling/unmarshalling objects
        # assume input is a dict. if instead it's a string assume dict in text (json)
        def load(data):
            if isinstance(data, str):
                return loads(data)

            dic, err = _Schema().load(data)
            return new_cls(**dic)


        def dump(self):
            ret, err = _Schema().dump(self)
            return ret


        def dumps(self):
            ret, err = _Schema().dumps(self)
            return ret


        setattr(new_cls, 'load', load)
        setattr(new_cls, 'loads', load)
        setattr(new_cls, 'dump', dump)
        setattr(new_cls, 'dumps', dumps)
        

        new_cls._schema = _Schema
        return new_cls


class JsonObject(metaclass=Meta):

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, vars(self))
