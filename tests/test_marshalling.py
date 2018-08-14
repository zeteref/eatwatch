import sys
import json
import unittest
from datetime import datetime
from meta import fields, JsonObject, post_load, MarshallError, InvalidFieldsError
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

    def test_invalid_fields(self):
        self.assertRaises(InvalidFieldsError, lambda: Test(invalid=True, error=False))

        try:
            Test(invalid=True, error=False)
        except InvalidFieldsError as e:
            self.assertIn('invalid', e.fields)
            self.assertIn('error', e.fields)
            self.assertEqual(len(e.fields), 2)



    def test_loading(self, use_objects=True):
        load = Test.load if use_objects else Test.loads
        prepare = lambda x: x if use_objects else json.dumps(x)

        self.assertRaises(MarshallError, lambda: load(prepare({'email':'test'})))

        ret = load(prepare({'email':'test@test.com'}))
        self.assertEqual(ret.email, 'test@test.com')


        ret = load(prepare({'date':'2010-10-20 23:59'}))
        self.assertEqual(ret.date, datetime(2010, 10, 20, 23, 59))

        self.assertRaises(MarshallError, lambda: load(prepare({'date':'2010-10-2023:59'})))


    def test_object_loading(self):
        self.test_loading(use_objects=True)


    def test_text_loading(self):
        self.test_loading(use_objects=False)


    def test_dumping(self, use_objects=True):
        dump = Test.dump if use_objects else Test.dumps
        prepare = lambda x: x if use_objects else json.loads(x)

        self.assertRaises(MarshallError, lambda: dump({'email':'test'}))

        ret = dump({'email':'test@test.com'})
        ret = prepare(ret)
        self.assertEqual(ret['email'], 'test@test.com')

        ret = dump({'date': datetime(2010, 10, 20, 23, 59)})
        ret = prepare(ret)
        self.assertEqual(ret['date'], '2010-10-20 23:59')


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
    date = fields.DateTime(
            format='%Y-%m-%d %H:%M')


class Due(JsonObject):
    id = fields.Int()
    name = fields.Str()
    unos = fields.List(fields.Nested(Uno))


class TestSimpleNestedList(unittest.TestCase):

    def test_simple_load_dict(self):
        dic = {'id': 1, 'name':'due', 'unos':[{'name':'uno', 'date':'2010-10-30 22:15'}]}
        
        test = Due.load(dic)

        self.assertEqual(test.id, 1)
        self.assertEqual(test.name, 'due')
        self.assertEqual(test.unos[0].name, 'uno')
        self.assertEqual(test.unos[0].date, datetime(2010, 10, 30, 22, 15))
        self.assertEqual(len(test.unos), 1)

        test_dic = test.dump()

        self.assertEqual(test_dic, dic)


    def test_simple_load_json(self):
        dic = {'id': 1, 'name':'due', 'unos':[{'name':'uno', 'date':'2010-10-30 22:15'}]}
        text = json.dumps(dic) # dump to string using standard json lib

        test = Due.loads(text) # load to object using marshmallow

        self.assertEqual(test.id, 1)
        self.assertEqual(test.name, 'due')
        self.assertEqual(test.unos[0].name, 'uno')
        self.assertEqual(len(test.unos), 1)

        test_text = test.dumps() # dump to text using marshmallow
        test_dic = json.loads(test_text) # load text to dic with standard json lib

        self.assertEqual(test_dic, dic)
