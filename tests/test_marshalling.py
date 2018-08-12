import sys
import json
import unittest
from datetime import datetime
from meta import fields, JsonObject, post_load
from model import *

sys.path.append('../')

class Test(JsonObject):
    id = fields.Int()
    name = fields.Str()
    quantity = fields.Float()
    email = fields.Email()
    date = fields.DateTime(
            format='%Y-%m-%d %H:%M', 
            missing=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    class Meta:
        ordered = True


class TestSimpleMarshalling(unittest.TestCase):

    def setUp(self):
        self.schema = Test._schema()


    def test_loading(self, use_objects=True):
        load = Test.load if use_objects else Test.loads
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


class TestSimpleClassesMarshalling(unittest.TestCase):

    def test_class_2_object(self):
        a = Test.load({'name':'hello'})
        self.assertEqual(a.name, 'hello')
        test_vars = vars(a)
        self.assertEqual(len(test_vars), 2)
        self.assertIn('name', test_vars)
        self.assertIn('date', test_vars)

        b = a.dump()
        self.assertEqual(b['name'], 'hello')
        self.assertIn('date', b)


    def test_class_2_text(self):
        a = Test.loads('{"name":"hello"}')
        self.assertEqual(a.name, 'hello')
        test_vars = vars(a)
        self.assertEqual(len(test_vars), 2)
        self.assertIn('date', test_vars)
        self.assertIn('name', test_vars)

        a = Test.load('{"name":"hello"}')
        self.assertEqual(a.name, 'hello')
        test_vars = vars(a)
        self.assertEqual(len(test_vars), 2)
        self.assertIn('date', test_vars)
        self.assertIn('name', test_vars)


        a = Test.load('{"date":"2010-11-22 22:59"}')
        self.assertEqual(a.date, datetime(2010, 11, 22, 22, 59))
        test_vars = vars(a)
        self.assertEqual(len(test_vars), 1)
        self.assertIn('date', test_vars)

        test_dic = a.dump()
        self.assertEqual(test_dic['date'], '2010-11-22 22:59')

        test_json = a.dumps()
        self.assertEqual(test_json, '{"date": "2010-11-22 22:59"}')

        test_cls = Test.load(test_json)
        self.assertEqual(test_cls.date, datetime(2010, 11, 22, 22, 59))


class Uno(JsonObject):
    name = fields.Str()


class Due(JsonObject):
    id = fields.Int()
    name = fields.Str()
    unos = fields.List(fields.Nested(Uno))


class TestSimpleNestedList(unittest.TestCase):

    def test_simple_load_dict(self):
        dic = {'id': 1, 'name':'due', 'unos':[{'name':'uno'}]}
        
        test = Due.load(dic)

        self.assertEqual(test.id, 1)
        self.assertEqual(test.name, 'due')
        self.assertEqual(test.unos[0].name, 'uno')
        self.assertEqual(len(test.unos), 1)

        test_dic = test.dump()

        self.assertEqual(test_dic, dic)


    def test_simple_load_json(self):
        dic = {'id': 1, 'name':'due', 'unos':[{'name':'uno'}]}
        converted_dic = Due.dump(dic) # convert fields to json serializable (ie.: DateTime field)

        text = json.dumps(converted_dic) # dump to string using standard json lib

        test = Due.loads(text) # load to object using marshmallow

        self.assertEqual(test.id, 1)
        self.assertEqual(test.name, 'due')
        self.assertEqual(test.unos[0].name, 'uno')
        self.assertEqual(len(test.unos), 1)

        test_text = test.dumps() # dump to text using marshmallow
        test_dic = json.loads(test_text) # load text to dic with standard json lib

        self.assertEqual(test_dic, converted_dic)
