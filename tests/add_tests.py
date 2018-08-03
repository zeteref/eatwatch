import unittest
import sys
import datetime

sys.path.append('../')

from main import *

class TestAddObjects(unittest.TestCase):

    dbname = 'example.db'

    @classmethod
    def setUpClass(cls):
        drop_db(cls.dbname)
        create_db(cls.dbname)


    @classmethod
    def tearDownClass(cls):
        drop_db(cls.dbname)


    def setUp(self):
        with sqliteconn() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM meal_ingredients')
            c.execute('DELETE FROM ingredients')
            c.execute('DELETE FROM meals')


    def test_add_ingredient(self):
        add = add_ingredient(ingredient('test', 
                                        calories='1',
                                        sugar='2',
                                        veg_protein=3,
                                        protein=4,
                                        carbo='5'))
        c = condition
        test = next(get_ingredients(c('id', '=', add.id)), None)
        self.assertEqual(test.id, add.id)

        self.assertEqual(test.calories, 1)
        self.assertEqual(test.sugar, 2)
        self.assertEqual(test.veg_protein, 3)
        self.assertEqual(test.protein, 4)
        self.assertEqual(test.carbo, 5)

        none = next(get_ingredients(c('id', '!=', add.id)), None)
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

