import sys
from backend import Storage
from model import *

class MealStorage(Storage):

    def add_ingredient(self, ingredient):
        return self.insert('ingredients', ingredient.dump(ignore=('id',)))


    def delete_ingredient(self, *conds):
        return self.delete('ingredients', conds)


    def get_ingredients(self, *conds):
        dics = self.select('ingredients', Ingredient.fields(), conds)
        return (Ingredient.load(dic) for dic in dics)


    def add_meal(self, meal):
        return self.add(meal)


    def delete_meal(self, meal):
        return self.delete(meal)


    def get_meals(self, *args):
        return self.select(Meal.fields(), *args)


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

        storage.drop_db()
        storage.create_db()


if __name__ == '__main__':
    __main__()
