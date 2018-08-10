import unittest
import sys
import json
from datetime import datetime

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

        self.storage.delete_ingredient(eq('id', id_))
        none = next(self.storage.get_ingredients(eq('id', id_)), None)
        self.assertIsNone(none)

        return test


    def test_add_meal(self):
        id_ = self.storage.add_meal(Meal(name='obiad',
                                         date=datetime(2001, 12, 1, 15, 45)))

        test = next(self.storage.get_meals(eq('id', id_)))
        self.assertEqual(test.name, 'obiad')
        self.assertEqual(test.date, datetime(2001, 12, 1, 15, 45))

        none = next(self.storage.get_meals(neq('id', id_)), None)
        self.assertIsNone(none)

        self.storage.delete_meal(eq('id', test.id))
        none = next(self.storage.get_meals(eq('id', id_)), None)
        self.assertIsNone(none)

        return test


    def test_add_meal_ingredient(self):
        ingr = self.test_add_ingredient()
        meal = self.test_add_meal()

        id_ = self.storage.add_meal_ingredient(MealIngredient(
            meal_id=meal.id,
            ingredient_id=ingr.id,
            quantity=87.5
        ))
        
        test = next(self.storage.get_meal_ingredients(eq('id', id_)), None)

        self.assertEqual(test.ingredient_id, ingr.id)
        self.assertEqual(test.meal_id, meal.id)
        self.assertEqual(test.quantity, 87.5)

        none = next(self.storage.get_meal_ingredients(neq('id', id_)), None)
        self.assertIsNone(none)

        self.storage.delete_meal_ingredient(eq('id', test.id))
        none = next(self.storage.get_meal_ingredients(eq('id', id_)), None)
        self.assertIsNone(none)

        return test
