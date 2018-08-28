"""
CherryPy-based webservice
"""

from __future__ import print_function

import threading
import json
import cherrypy

from cherrypy.lib import auth_basic
from cherrypy.process import plugins

from sqlite3_engine import SQLite3Engine
from meal_storage import MealStorage
from model import *
from conditions import *
from utils import first 


def cors():
    
    if cherrypy.request.method in('OPTIONS', 'OPTONS'): # firefox HTTP Request Maker sends OPTONS ???
        # preflign request 
        # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
        cherrypy.response.headers['Access-Control-Allow-Origin']  = '*'
        # tell CherryPy to avoid normal handler
        return True
    else:
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)

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
        print(request_data)


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
        conditions = [like(key, '%'+value+'%') for (key, value) in kwds.items() if key in Meal.columns()]
        
        return [x.dump() for x in self.storage.get_meals(*conditions)]


def jsonify_error(status, message, traceback, version):
    """JSONify all CherryPy error responses (created by raising the
    cherrypy.HTTPError exception)
    """

    cherrypy.response.headers['Content-Type'] = 'application/json'
    response_body = json.dumps(
        {
            'error': {
                'http_status': status,
                'message': message,
            }
        })

    cherrypy.response.status = status

    return response_body


def validate_password(realm, username, password):
    """
    Simple password validation
    """
    return username in USERS and USERS[username] == password


if __name__ == '__main__':

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # /meals (GET)
    dispatcher.connect(name='meals',
                       route='/meals',
                       action='get_meals',
                       controller=MealsController(),
                       conditions={'method': ['GET']})

    # /meals/{id} (GET)
    #
    # Request "/nodes/notfound" (GET) to test the 404 (not found) handler
    dispatcher.connect(name='meals',
                       route='/meals/{id}',
                       action='get_meal',
                       controller=MealsController(),
                       conditions={'method': ['GET']})


    dispatcher.connect(name='meals',
                       route='/meals/{meal_id}/ingredients',
                       action='get_meal_ingredients',
                       controller=MealsController(),
                       conditions={'method': ['GET']})

    # /nodes/{name} (POST)
    dispatcher.connect(name='meals',
                       route='/meals',
                       action='add_meal',
                       controller=MealsController(),
                       conditions={'method': ['POST']})

    # /nodes/{name} (PUT)
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='update_node',
                       controller=MealsController(),
                       conditions={'method': ['PUT']})

    # /nodes/{name} (DELETE)
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='delete_node',
                       controller=MealsController(),
                       conditions={'method': ['DELETE']})


    # INGREDIETNS
    dispatcher.connect(name='ingredients',
                       route='/ingredients',
                       action='get_ingredients',
                       controller=MealsController(),
                       conditions={'method': ['GET']})


    dispatcher.connect(name='ingredients',
                       route='/ingredients',
                       action='add_ingredient',
                       controller=MealsController(),
                       conditions={'method': ['POST']})


    dispatcher.connect(name='ingredients',
                       route='/ingredients/{id}',
                       action='get_ingredient',
                       controller=MealsController(),
                       conditions={'method': ['GET']})


    # MEAL INGREDIENTS


    dispatcher.connect(name='search',
                       route='/search',
                       action='search',
                       controller=MealsController(),
                       conditions={'method': ['GET']})
    config = {
        'global': {
            'engine.autoreload.on': True
        },
        '/': {
            'request.dispatch': dispatcher,
            'error_page.default': jsonify_error,
            'tools.cors.on' : True,
            'tools.json_in.on': True,
            'tools.json_out.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        },
    }

    cherrypy.tree.mount(root=None, config=config)

    cherrypy.config.update({
        'engine.autoreload.on' : True,
        # 'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    })

    cherrypy.config.update({
        'global': {
            'engine.autoreload.on' : True
        }
    })




    cherrypy.config.update({
        '/': {
        }
    })

    cherrypy.engine.start()
    cherrypy.engine.block()
    #cherrypy.quickstart()
