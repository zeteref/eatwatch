"""
CherryPy-based webservice
"""

import json
import cherrypy

import routeconfig
from sqlite3_engine import SQLite3Engine
from meal_storage import MealStorage
from model import *
from conditions import *
from utils import first 


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


def cors():
    if cherrypy.request.method in ('OPTIONS', 'OPTONS'): # firefox HTTP Request Maker sends OPTONS ???
        # preflign request 
        # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
        cherrypy.response.headers['Access-Control-Allow-Origin']  = '*'
        # tell CherryPy to avoid normal handler
        return True
    else:
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'


def start():
    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    routeconfig.init(dispatcher)

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
    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    start()
