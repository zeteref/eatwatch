import sys

from pathlib import Path

from backend import Storage
from model import *


class MealStorage(Storage):

    def __init__(self, constr):
        super().__init__(constr)

        if not Path(self.constr).is_file():
            self.create_db()


    def add_ingredient(self, ingredient):
        return self.insert('ingredients', ingredient.dump(ignore=('id',)))


    def delete_ingredient(self, *conds):
        return self.delete('ingredients', conds)


    def get_ingredients(self, *conds):
        dics = self.select('ingredients', Ingredient.columns(), conds)
        return (Ingredient.load(dic) for dic in dics)


    def add_meal(self, meal):
        return self.insert('meals', meal.dump(ignore=('id',)))


    def delete_meal(self, *conds):
        return self.delete('meals', conds)


    def get_meals(self, *conds):
        dics = self.select('meals', Meal.columns(), conds)
        return (Meal.load(dic) for dic in dics)


    def add_meal_ingredient(self, meal_ingredient):
        return self.insert('meal_ingredients', meal_ingredient.dump(ignore=('id',)))


    def delete_meal_ingredient(self, *conds):
        return self.delete('meal_ingredients', conds)


    def get_meal_ingredients(self, *conds):
        dics = self.select('meal_ingredients', MealIngredient.columns(), conds)
        return (MealIngredient.load(dic) for dic in dics)


def __main__():
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        dbname = sys.argv[2] if len(sys.argv) > 2 else 'example.db'
        storage = MealStorage(dbname)

        storage.drop_db()
        storage.create_db()


if __name__ == '__main__':
    __main__()
