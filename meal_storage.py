import sys

from sql_storage import SQLStorage 
from model import *
from conditions import *
from utils import extract, first


class MealStorage():

    def __init__(self, engine):
        self.sqlstorage = SQLStorage(engine)


    def clear(self):
        self.sqlstorage.execute_ddl((
            'DELETE FROM meal_ingredients',
            'DELETE FROM ingredients',
            'DELETE FROM meals'))


    def delete(self):
        
        ddl = [
            'DROP TABLE meal_ingredients',
            'DROP TABLE ingredients',
            'DROP TABLE meals'
        ]

        for stmt in ddl:
            try:
                self.sqlstorage.execute_ddl((stmt,))
            except:
                pass


    def init(self):
        self.sqlstorage.execute_ddl((
                """
                    CREATE TABLE ingredients (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        calories FLOAT DEFAULT 0 NOT NULL,
                        fats FLOAT DEFAULT 0 NOT NULL,
                        sugar FLOAT DEFAULT 0 NOT NULL,
                        veg_protein FLOAT DEFAULT 0 NOT NULL,
                        protein FLOAT DEFAULT 0 NOT NULL,
                        carbo FLOAT DEFAULT 0 NOT NULL
                    )
                """,
                """
                    CREATE TABLE meals (
                        id INTEGER PRIMARY KEY,
                        date TEXT NOT NULL,
                        name TEXT
                    )
                """,
                """
                    CREATE TABLE meal_ingredients (
                        id INTEGER PRIMARY KEY,
                        ingredient_id INTEGER NOT NULL,
                        meal_id INTEGER NOT NULL,
                        quantity FLOAT NOT NULL,
                        FOREIGN KEY(meal_id) REFERENCES meal(id)
                        FOREIGN KEY(ingredient_id) REFERENCES ingredient(id)
                    )
                """))


    def add_ingredient(self, ingredient):
        id_ = self.sqlstorage.insert('ingredients', ingredient.dump(ignore=('id',)))
        ingredient.id = id_
        return ingredient


    def add_ingredients(self, ingredients):
        return [self.add_ingredient(x) for x in ingredients if not hasattr(x,'id')]


    def delete_ingredient(self, *conds):
        return self.sqlstorage.delete('ingredients', conds)


    def get_ingredients(self, *conds):
        dics = self.sqlstorage.select('ingredients', Ingredient.columns(), conds)
        return [Ingredient.load(dic) for dic in dics]


    def get_ingredient(self, id):
        return first(self.get_ingredients(eq('id', id)))


    def add_meal(self, meal):
        id_ = self.sqlstorage.insert('meals', meal.dump(ignore=('id', 'meal_ingredients')))
        meal.id = id_

        for mi in meal.meal_ingredients:
            mi.meal_id = meal.id
            self.add_meal_ingredient(mi)

        return meal


    def delete_meal(self, *conds):
        return self.sqlstorage.delete('meals', conds)


    def get_meals(self, *conds):
        dics = self.sqlstorage.select('meals', Meal.columns(), conds)
        return [Meal.load(dic) for dic in dics]


    def get_meal(self, id):
        return first(self.get_meals(eq('id', id)))


    def add_meal_ingredient(self, meal_ingredient):
        ing = meal_ingredient.ingredient

        if ing is not None:
            if not hasattr(ing, 'id'):
                ing = self.add_ingredient(ing)
            meal_ingredient.ingredient_id = ing.id

        id_ = self.sqlstorage.insert('meal_ingredients', meal_ingredient.dump(ignore=('id', 'ingredient')))
        meal_ingredient.id = id_

        return meal_ingredient


    def delete_meal_ingredient(self, *conds):
        return self.sqlstorage.delete('meal_ingredients', conds)


    def get_meal_ingredients(self, *conds):
        dics = self.sqlstorage.select('meal_ingredients', MealIngredient.columns(), conds)
        return [MealIngredient.load(dic) for dic in dics]
