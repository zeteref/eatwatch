import json
import cherrypy

from sqlite3_engine import SQLite3Engine
from meal_storage import MealStorage
from model import *
from conditions import *
from utils import first 

class MealsController(object):
    def __init__(self):
        self.storage = MealStorage(SQLite3Engine('e.db'))

    # INGREDIENTS

    @cherrypy.tools.accept(media='application/json')
    def get_ingredients(self):
        """
        Handler for /meals (GET)
        """

        return [x.dump() for x in self.storage.get_ingredients()]


    @cherrypy.tools.accept(media='application/json')
    def add_ingredient(self):
        request_data = cherrypy.request.json
        ingredient = Ingredient.load(request_data)
        ret = self.storage.add_ingredient(ingredient)
        return ret.dump()


    @cherrypy.tools.accept(media='application/json')
    def update_ingredient(self):
        request_data = cherrypy.request.json
        ingredient = Ingredient.load(request_data)
        ret = self.storage.update_ingredient(ingredient)
        return ret.dump()


    def delete_ingredient(self, id):
        ret = self.storage.delete_ingredient(id=id)


    def get_ingredient(self, id):
        """
        Handler for /ingredients/<id> (GET)
        """
        ret = first(self.storage.get_ingredients(eq('id', id)))

        if ret is None:
            raise cherrypy.HTTPError(404, 'Ingredient id:\"{0}\" not found'.format(id))

        return ret.dump()

    # MEAL INGREDIENTS

    @cherrypy.tools.accept(media='application/json')
    def get_meal_ingredients(self, meal_id):
        """
        Handler for /meals/<meal_id>/ingredients (GET)
        """

        meal_ingredients = self.storage.get_meal_ingredients(eq('meal_id', meal_id))
        for mi in meal_ingredients:
            mi.ingredient = self.storage.get_ingredient(mi.ingredient_id)

        return [x.dump() for x in meal_ingredients]


    # MEALS

    @cherrypy.tools.accept(media='application/json')
    def get_meals(self):
        """
        Handler for /meals (GET)
        """

        return [x.dump() for x in self.storage.get_meals()]


    def get_meal(self, id):
        """
        Handler for /meals/<name> (GET)
        """
        ret = self.storage.get_meal(id)
        if ret is None:
            raise cherrypy.HTTPError(404, 'Meal id:\"{0}\" not found'.format(id))

        return ret.dump()


    def add_meal(self):
        """
        Handler for /nodes (POST)
        """

        request_data = cherrypy.request.json
        meal = Meal.load(request_data)

        errors = []
        if errors:
            # Attempt to format errors dict from Marshmallow
            errmsg = ', '.join(
                ['Key: [{0}], Error: {1}'.format(key, error)
                 for key, error in errors.items()])

            raise cherrypy.HTTPError(
                400, 'Malformed POST request data: {0}'.format(errmsg))

        id_ = self.storage.add_meal(meal)
        meal.id = id_
        return meal.dump()


    def update_node(self, name):
        """
        Handler for /nodes/<name> (PUT)
        """

        if name not in sample_nodes:
            raise cherrypy.HTTPError(
                404, 'Node \"{0}\" not found'.format(name))

        # Empty response (http status 204) for successful PUT request
        cherrypy.response.status = 204

        return ''

    def delete_node(self, name):
        """
        Handler for /nodes/<name> (DELETE)
        """

        # TODO: handle DELETE here

        # Empty response (http status 204) for successful DELETE request
        cherrypy.response.status = 204

        return ''


    def search(self, q, **kwds):
        table = q
        if q == 'meals':
            conditions = [like(key, '%'+value+'%') for (key, value) in kwds.items() if key in Meal.columns()]
            return [x.dump() for x in self.storage.get_meals(*conditions)]
        elif q == 'ingredients':
            conditions = [like(key, '%'+value+'%') for (key, value) in kwds.items() if key in Ingredient.columns()]
            return [x.dump() for x in self.storage.get_ingredients(*conditions)]
