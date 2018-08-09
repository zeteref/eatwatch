import unittest
import json
from datetime import datetime

from marshmallow import Schema, fields, post_load


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

        def load(data):
            dic, err = _Schema().load(data)
            return new_cls(**dic)
        
        setattr(new_cls, 'load', load)

        def dump(self):
            return _Schema().dump(self)

        setattr(new_cls, 'dump', dump)

        new_cls._schema = _Schema
        return new_cls


class JsonObject(metaclass=Meta):
    pass


class Test(JsonObject):
    id = fields.Int()
    name = fields.Str()
    quantity = fields.Float()
    email = fields.Email()
    date = fields.DateTime(
            format='%Y-%m-%d %H:%M', 
            missing=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))


t = Test.load({'name':'hello'})
print(Test._schema().dumps(t))
#t, e = Test._schema().load({'name':'hello'})
##
#print(t, e)


class TestSimpleMarshalling(unittest.TestCase):

    def setUp(self):
        self.schema = Test._schema()


    def test_loading(self, use_objects=True):
        schema = self.schema
        load = schema.load if use_objects else schema.loads
        prepare = lambda x: x if use_objects else json.dumps(x)

        ret, err = load(prepare({'email':'test'}))
        self.assertIn('email', err)

        ret, err = load(prepare({'email':'test@test.com'}))
        self.assertEqual(ret['email'], 'test@test.com')
        self.assertEqual(err, {})


        ret, err = load(prepare({'date':'2010-10-20 23:59'}))
        self.assertEqual(ret['date'], datetime(2010, 10, 20, 23, 59))
        self.assertEqual(err, {})

        ret, err = load(prepare({'date':'2010-10-2023:59'}))
        self.assertIn('date', err)


    def test_object_loading(self):
        self.test_loading(use_objects=True)


    def test_text_loading(self):
        self.test_loading(use_objects=False)


    def test_dumping(self, use_objects=True):
        schema = self.schema
        dump = schema.dump if use_objects else schema.dumps
        prepare = lambda x: x if use_objects else json.loads(x)

        ret, err = dump({'email':'test'})
        self.assertIn('email', err)
        err.pop('email')
        self.assertEqual(err, {})

        ret, err = dump({'email':'test@test.com'})
        ret = prepare(ret)
        self.assertEqual(ret['email'], 'test@test.com')
        self.assertEqual(err, {})

        ret, err = dump({'date': datetime(2010, 10, 20, 23, 59)})
        ret = prepare(ret)
        self.assertEqual(ret['date'], '2010-10-20 23:59')
        self.assertEqual(err, {})

        ret, err = schema.dump({'date': '2010-10-20 23:59'})
        self.assertIn('date', err)
        err.pop('date')
        self.assertEqual(err, {})


    def test_object_dumping(self):
        self.test_dumping(use_objects=True)


    def test_text_dumping(self):
        self.test_dumping(use_objects=False)
