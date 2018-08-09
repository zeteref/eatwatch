import sys
from backend import Storage
from model import *

class MealStorage(Storage):

    def init(self):
        self.create_db()


    def clear(self):
        self.drop_db()


    def add_ingredient(self, ingredient):
        return self.add(ingredient)


    def delete_ingredient(self, ingredient):
        return self.delete(ingredient)


    def get_ingredients(self, *args):
        return self.get(Ingredient, *args)


    def add_meal(self, meal):
        return self.add(meal)


    def delete_meal(self, meal):
        return self.delete(meal)


    def get_meals(self, *args):
        return self.get(Meal, *args)


    def add_meal_ingredient(self, meal_ingredient):
        return self.add(meal_ingredient)


    def delete_meal_ingredient(self, meal_ingredient):
        return self.delete(meal_ingredient)


    def get_meal_ingredients(self, *args):
        return self.get(MealIngredient, *args)


def __main__():
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        dbname = sys.argv[2] if len(sys.argv) > 2 else 'example.db'
        storage = MealStorage(dbname)

        storage.clear()
        storage.init()


if __name__ == '__main__':
    __main__()
