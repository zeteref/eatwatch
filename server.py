"""
CherryPy-based webservice
"""

from __future__ import print_function

import threading
import json
import cherrypy
import cherrypy_cors

from pathlib import Path

from cherrypy.lib import auth_basic
from cherrypy.process import plugins
from marshmallow import Schema, fields

from storage import MealStorage
from model import *
from conditions import *

class MealsController(object):
    def __init__(self):
        self.storage = MealStorage('example.db')


    @cherrypy.tools.json_out()
    @cherrypy.tools.accept(media='application/json')
    def get_all(self):
        """
        Handler for /meals (GET)
        """

        return [x.dump() for x in self.storage.get_meals()]


    @cherrypy.tools.json_out()
    def get(self, name):
        """
        Handler for /nodes/<name> (GET)
        """

        if name not in sample_nodes:
            raise cherrypy.HTTPError(
                404, 'Node \"{0}\" not found'.format(name))

        return [{'name': name}]


    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
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


    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
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

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete_node(self, name):
        """
        Handler for /nodes/<name> (DELETE)
        """

        # TODO: handle DELETE here

        # Empty response (http status 204) for successful DELETE request
        cherrypy.response.status = 204

        return ''


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
    cherrypy_cors.install()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # /meals (GET)
    dispatcher.connect(name='meals',
                       route='/meals',
                       action='get_all',
                       controller=MealsController(),
                       conditions={'method': ['GET']})

    # /nodes/{name} (GET)
    #
    # Request "/nodes/notfound" (GET) to test the 404 (not found) handler
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='get',
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

    config = {
        'global': {
            'engine.autoreload.on': True
        },
        '/': {
            'request.dispatch': dispatcher,
            'error_page.default': jsonify_error,
            'cors.expose.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],

            #'tools.auth_basic.on': True,
            #'tools.auth_basic.realm': 'localhost',
            #'tools.auth_basic.checkpassword': validate_password,
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

    cherrypy.engine.start()
    cherrypy.engine.block()
    #cherrypy.quickstart()
