import unittest
import sys
import json
import datetime

sys.path.append('../')

from model import *
from storage import MealStorage
from conditions import *

class TestAddObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage = MealStorage('example.db')
        cls.storage.drop_db()
        cls.storage.create_db()


    @classmethod
    def tearDownClass(cls):
        cls.storage.clear_db()


    def setUp(self):
        self.storage.clear_db()


    def test_add_ingredient(self):
        id_ = self.storage.add_ingredient(Ingredient(name='test', 
                                                     calories=1.1,
                                                     sugar=2.2,
                                                     veg_protein=3.3,
                                                     protein=4.4,
                                                     carbo=5.5))


        test = next(self.storage.get_ingredients(eq('id', id_)), None)

        self.assertEqual(test.id, id_)
        self.assertEqual(test.calories, 1.1)
        self.assertEqual(test.sugar, 2.2)
        self.assertEqual(test.veg_protein, 3.3)
        self.assertEqual(test.protein, 4.4)
        self.assertEqual(test.carbo, 5.5)

        none = next(self.storage.get_ingredients(neq('id', id_)), None)
        self.assertIsNone(none)

        return test


    def test_add_meal(self):
        add = add_meal(meal('obiad', datetime(2001, 12, 1, 15, 45).isoformat()))

        c = condition
        test = next(get_meals(c('id', '=', add.id)))

        self.assertEqual('obiad', test.name)
        self.assertEqual(add.date, datetime.strptime(test.date, "%Y-%m-%dT%H:%M:%S").isoformat())

        none = next(get_meals(c('id', '!=', add.id)), None)
        self.assertIsNone(none)

        return test


    def test_add_meal_ingredient(self):
        ingr = self.test_add_ingredient()
        meal = self.test_add_meal()

        add = add_meal_ingredient(meal_ingredient(ingredient_id=ingr.id, meal_id=meal.id, quantity=87.3))
        
        c = condition
        test = next(get_meal_ingredients(c('id', '=', add.id)), None)

        self.assertEqual(add.ingredient_id, test.ingredient_id)
        self.assertEqual(add.meal_id, test.meal_id)
        self.assertEqual(87.3, test.quantity)

        none = next(get_meal_ingredients(c('id', '!=', add.id)), None)
        self.assertIsNone(none)

        return test


    def test_delete_ingredient(self):
        to_delete = self.test_add_ingredient()
        self.assertIsNotNone(to_delete.id)

        delete_ingredient(to_delete)

        c = condition
        none = next(get_ingredients(c('id', '=', to_delete.id)), None)
        self.assertIsNone(none)


    def test_delete_meal(self):
        to_delete = self.test_add_meal()
        self.assertIsNotNone(to_delete.id)

        delete_meal(to_delete)

        c = condition
        none = next(get_meals(c('id', '=', to_delete.id)), None)
        self.assertIsNone(none)


    def test_delete_meal_ingredient(self):
        to_delete = self.test_add_meal_ingredient()
        self.assertIsNotNone(to_delete.id)

        delete_meal_ingredient(to_delete)

        c = condition
        none = next(get_meal_ingredients(c('id', '=', to_delete.id)), None)
        self.assertIsNone(none)


class TestJsonSerialization(unittest.TestCase):

    def test_simple_serialization(self):
        dumped, errors = MealSchema().dumps({"date":datetime(2017, 1, 25, 13, 40, 0), "name":"obiad" })
        self.assertEqual(dumped, '{"name": "obiad", "date": "2017-01-25 13:40"}')

        test, errors  = MealSchema().loads(dumped)
        self.assertEqual(test.name, 'obiad')
        self.assertEqual(test.date, datetime(2017, 1, 25, 13, 40, 0))
