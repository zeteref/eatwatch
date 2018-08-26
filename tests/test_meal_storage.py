import unittest
import sys
import json
from datetime import datetime

sys.path.append('../')

from model import *
from sqlite3_engine import SQLite3Engine
from meal_storage import MealStorage
from conditions import *
from utils import first, extract, today_at

class TestAddObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage = MealStorage(SQLite3Engine('test.db'))
        cls.storage.delete()
        cls.storage.init()


    @classmethod
    def tearDownClass(cls):
        cls.storage.clear()


    def setUp(self):
        self.storage.clear()


    def test_add_ingredient(self):
        added = self.storage.add_ingredient(Ingredient(
            name='test', 
            calories=1.1,
            sugar=2.2,
            veg_protein=3.3,
            protein=4.4,
            carbo=5.5))

        test = first(self.storage.get_ingredients(eq('id', added.id)))

        self.assertEqual(test.id, added.id)
        self.assertEqual(test.calories, 1.1)
        self.assertEqual(test.sugar, 2.2)
        self.assertEqual(test.veg_protein, 3.3)
        self.assertEqual(test.protein, 4.4)
        self.assertEqual(test.carbo, 5.5)

        none = first(self.storage.get_ingredients(neq('id', added.id)))
        self.assertIsNone(none)

        self.storage.delete_ingredient(eq('id', added.id))
        none = first(self.storage.get_ingredients(eq('id', added.id)))
        self.assertIsNone(none)

        return test


    def test_add_meal(self):
        added = self.storage.add_meal(Meal(
            name='obiad',
            date=datetime(2001, 12, 1, 15, 45)))

        test = first(self.storage.get_meals(eq('id', added.id)))
        self.assertEqual(test.name, 'obiad')
        self.assertEqual(test.date, datetime(2001, 12, 1, 15, 45))

        none = first(self.storage.get_meals(neq('id', added.id)))
        self.assertIsNone(none)

        self.storage.delete_meal(eq('id', test.id))
        none = first(self.storage.get_meals(eq('id', added.id)))
        self.assertIsNone(none)

        return test


    def test_add_meal_ingredient(self):
        ingr = self.test_add_ingredient()
        meal = self.test_add_meal()

        meal_ingredient = self.storage.add_meal_ingredient(MealIngredient(
            meal_id=meal.id,
            ingredient_id=ingr.id,
            quantity=87.5
        ))
        
        test = first(self.storage.get_meal_ingredients(eq('id', meal_ingredient.id)))

        self.assertEqual(test.ingredient_id, ingr.id)
        self.assertEqual(test.meal_id, meal.id)
        self.assertEqual(test.quantity, 87.5)

        none = first(self.storage.get_meal_ingredients(neq('id', meal_ingredient.id)))
        self.assertIsNone(none)

        self.storage.delete_meal_ingredient(eq('id', test.id))
        none = first(self.storage.get_meal_ingredients(eq('id', meal_ingredient.id)))
        self.assertIsNone(none)

        return test

class TestAddNestedObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage = MealStorage(SQLite3Engine('test.db'))
        cls.storage.delete()
        cls.storage.init()


    @classmethod
    def tearDownClass(cls):
        cls.storage.clear()


    def setUp(self):
        self.storage.clear()


    def create_some_ingredients(self):
        ret = []
        ret.extend([
            Ingredient(name='jajka', calories=139, protein=12.5, carbo=0.6, fats=9.7),
            Ingredient(name='łosoś wędzony', calories=162, protein=21.5, carbo=0.6, fats=18.1),
            Ingredient(name='avocado', calories=160, veg_protein=2.0, carbo=8.5, fats=14.7)])
        return ret


    def test_add_ingredients(self):
        ingredients = self.create_some_ingredients()
        ret = self.storage.add_ingredients(ingredients)

        for ingr in ret:
            self.assertNotEqual(ingr.id, None)


    def test_add_meal_with_new_ingredients(self):
        ingredients = self.create_some_ingredients()

        meal = Meal(name='śniadanie', date=today_at('9:00'), meal_ingredients=[
            MealIngredient(ingredient=ingredients[0], quantity=60),
            MealIngredient(ingredient=ingredients[1], quantity=15),
            MealIngredient(ingredient=ingredients[2], quantity=20)
        ])

        test_mi = list(self.storage.get_meal_ingredients())
        self.assertEqual(len(test_mi), 0)

        test_i = list(self.storage.get_ingredients())
        self.assertEqual(len(test_i), 0)

        test_m = list(self.storage.get_meals())
        self.assertEqual(len(test_i), 0)
        
        self.storage.add_meal(meal)

        test_mi = list(self.storage.get_meal_ingredients())
        self.assertEqual(len(test_mi), 3)

        test_i = list(self.storage.get_ingredients())
        self.assertEqual(len(test_i), 3)

        test_m = list(self.storage.get_meals())
        self.assertEqual(len(test_m), 1)
        

    def test_add_meal_with_existing_ingredients(self):
        ingredients = self.create_some_ingredients()
        ingredients = self.storage.add_ingredients(ingredients)

        test_mi = list(self.storage.get_meal_ingredients())
        self.assertEqual(len(test_mi), 0)

        test_i = list(self.storage.get_ingredients())
        self.assertEqual(len(test_i), 3)

        test_m = list(self.storage.get_meals())
        self.assertEqual(len(test_m), 0)

        meal = Meal(name='śniadanie', date=today_at('9:00'), meal_ingredients=[
            MealIngredient(ingredient=ingredients[0], quantity=60),
            MealIngredient(ingredient=ingredients[1], quantity=15),
            MealIngredient(ingredient=ingredients[2], quantity=20)
        ])

        self.storage.add_meal(meal)


        test_mi = list(self.storage.get_meal_ingredients())
        self.assertEqual(len(test_mi), 3)

        test_i = list(self.storage.get_ingredients())
        self.assertEqual(len(test_i), 3)

        test_m = list(self.storage.get_meals())
        self.assertEqual(len(test_m), 1)
