import unittest
import json
from datetime import datetime

from marshmallow import Schema, fields, post_load

# TODO: send pull request or wait for fix in fields.py:911
DATEFORMAT='%Y-%m-%d %H:%M'
fields.DateTime.DATEFORMAT_SERIALIZATION_FUNCS[DATEFORMAT] = lambda value, localtime: value.strftime(DATEFORMAT)

class TestSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    quantity = fields.Float()
    email = fields.Email()
    date = fields.DateTime(
            format=DATEFORMAT, 
            missing=lambda: datetime.now().strftime(DATEFORMAT))


class Meta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super(Meta, mcs).__new__(mcs, name, bases, namespace, **kwargs)
        user_init = new_cls.__init__
        def __init__(self, *args, **kwargs):
            print("New __init__ called")
            user_init(self, *args, **kwargs)
            self.extra()
        print("Replacing __init__")
        setattr(new_cls, '__init__', __init__)
        return new_cls


class TestSimpleMarshalling(unittest.TestCase):

    def setUp(self):
        self.schema = TestSchema()


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

        ret, err = dump({'email':'test@test.com'})
        ret = prepare(ret)
        self.assertEqual(ret['email'], 'test@test.com')

        ret, err = dump({'date': datetime(2010, 10, 20, 23, 59)})
        ret = prepare(ret)
        self.assertEqual(ret['date'], '2010-10-20 23:59')

        ret, err = schema.dump({'date': '2010-10-20 23:59'})
        self.assertIn('date', err)


    def test_object_dumping(self):
        self.test_dumping(use_objects=True)


    def test_text_dumping(self):
        self.test_dumping(use_objects=False)
