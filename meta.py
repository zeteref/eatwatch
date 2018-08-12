import json
from datetime import datetime
import marshmallow

__all__ = ['JsonObject', 'fields', 'post_load']

def _fix_for_marshmallow_datetime_serialization(_fields):
    # TODO: send pull request or wait for fix in fields.py:911
    _date_fields = [x for (_, x) in _fields.items() if isinstance(x, marshmallow.fields.DateTime)]
    for _date_field in _date_fields:
        if hasattr(_date_field, 'dateformat'):
            def _strftime(value, localtime):
                return value.strftime(_date_field.dateformat)

            marshmallow.fields.DateTime.DATEFORMAT_SERIALIZATION_FUNCS[_date_field.dateformat] = _strftime


class Meta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        _fix_for_marshmallow_datetime_serialization(namespace)
        schema_fields = [(k,v) for (k,v) in namespace.items() if isinstance(v, marshmallow.fields.Field)]
        namespace = dict([(k,v) for (k,v) in namespace.items() if not isinstance(v, marshmallow.fields.Field)])

        if 'make_user' in namespace:
            schema_fields.append(('make_user', namespace.pop('make_user')))

        new_cls = super(Meta, mcs).__new__(mcs, name, bases, namespace, **kwargs)

        def __init__(self, **data):
            for k,v in data.items():
                setattr(self, k, v)

        setattr(new_cls, '__init__', __init__)


        def _make_obj(self, data):
            return new_cls(**data)

        schema_fields.append(('make_obj', marshmallow.post_load(_make_obj)))

        _Schema = type(name+'Schema', (marshmallow.Schema,), dict(schema_fields))


        def _fields():
            return [k for (k,v) in schema_fields]




        def loads(data):
            obj, err = _Schema().loads(data)
            return obj
        

        # since we will be *only* marshalling/unmarshalling objects
        # assume input is a dict. if instead it's a string assume dict in text (json)
        def load(data):
            if isinstance(data, str):
                return loads(data)

            obj, err = _Schema().load(data)
            return obj


        def dump(self, ignore=None):
            ret, err = _Schema().dump(self)

            if ignore is not None:
                for key in ignore:
                    if key in ret: 
                        ret.pop(key)

            return ret


        def dumps(self):
            ret, err = _Schema().dumps(self)
            return ret


        setattr(new_cls, 'load', load)
        setattr(new_cls, 'loads', load)
        setattr(new_cls, 'dump', dump)
        setattr(new_cls, 'dumps', dumps)
        setattr(new_cls, 'fields', _fields)


        new_cls._schema = _Schema
        return new_cls


class JsonObject(metaclass=Meta):

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, vars(self))


class Fields():
    def __getattr__(self, name):
        class Nested(marshmallow.fields.Nested):
            def __init__(self, jsonobj):
                return super().__init__(jsonobj._schema)

        if name == 'Nested':
            return Nested

        return getattr(marshmallow.fields, name)

# define names for imports (and __all__)
fields = Fields()
post_load = marshmallow.post_load
