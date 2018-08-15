import sys

from pathlib import Path

from backend import Storage
from model import *
from conditions import *
from utils import extract, first


class MealStorage(Storage):

    def __init__(self, constr):
        super().__init__(constr)

        if not Path(self.constr).is_file():
            self.create_db()


    def add_ingredient(self, ingredient):
        id_ = self.insert('ingredients', ingredient.dump(ignore=('id',)))
        ingredient.id = id_
        return ingredient


    def add_ingredients(self, ingredients):
        return [self.add_ingredient(x) for x in ingredients if not hasattr(x,'id')]


    def delete_ingredient(self, *conds):
        return self.delete('ingredients', conds)


    def get_ingredients(self, *conds):
        dics = self.select('ingredients', Ingredient.columns(), conds)
        return [Ingredient.load(dic) for dic in dics]


    def get_ingredient(self, id):
        return first(self.get_ingredients(eq('id', id)))


    def add_meal(self, meal):
        id_ = self.insert('meals', meal.dump(ignore=('id', 'meal_ingredients')))
        meal.id = id_

        for mi in meal.meal_ingredients:
            mi.meal_id = meal.id
            self.add_meal_ingredient(mi)

        return meal


    def delete_meal(self, *conds):
        return self.delete('meals', conds)


    def get_meals(self, *conds):
        dics = self.select('meals', Meal.columns(), conds)
        return [Meal.load(dic) for dic in dics]


    def get_meal(self, id):
        return first(self.get_meals(eq('id', id)))


    def add_meal_ingredient(self, meal_ingredient):
        ing = meal_ingredient.ingredient

        if ing is not None:
            if not hasattr(ing, 'id'):
                ing = self.add_ingredient(ing)
            meal_ingredient.ingredient_id = ing.id

        id_ = self.insert('meal_ingredients', meal_ingredient.dump(ignore=('id', 'ingredient')))
        meal_ingredient.id = id_

        return meal_ingredient



    def delete_meal_ingredient(self, *conds):
        return self.delete('meal_ingredients', conds)


    def get_meal_ingredients(self, *conds):
        dics = self.select('meal_ingredients', MealIngredient.columns(), conds)
        return [MealIngredient.load(dic) for dic in dics]


def __main__():
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        dbname = sys.argv[2] if len(sys.argv) > 2 else 'example.db'
        storage = MealStorage(dbname)

        storage.drop_db()
        storage.create_db()


if __name__ == '__main__':
    __main__()
