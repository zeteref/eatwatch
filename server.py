#!/usr/bin/env python

# pylint: disable=invalid-name

"""
CherryPy-based webservice daemon with background threads
"""

from __future__ import print_function
import threading
import json
import cherrypy
from cherrypy.lib import auth_basic  # noqa pylint: disable=unused-import
from cherrypy.process import plugins
import cherrypy_cors
from marshmallow import Schema, fields

sample_nodes = [
    'node1',
    'node2',
]


class NodeSchema(Schema):
    """
    Marshmallow schema for nodes object
    """
    name = fields.String(required=True)


class NodesController(object): \
        # pylint: disable=too-few-public-methods

    """Controller for fictional "nodes" webservice APIs"""

    @cherrypy.tools.json_out()
    @cherrypy.tools.accept(media='application/json')
    def get_all(self): \
            # pylint: disable=no-self-use
        """
        Handler for /nodes (GET)
        """
        return [{'name': name} for name in sample_nodes]

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
    def add_node(self): \
            # pylint: disable=no-self-use
        """
        Handler for /nodes (POST)
        """

        request_data = cherrypy.request.json

        data, errors = NodeSchema().load(request_data)

        if errors:
            # Attempt to format errors dict from Marshmallow
            errmsg = ', '.join(
                ['Key: [{0}], Error: {1}'.format(key, error)
                 for key, error in errors.items()])

            raise cherrypy.HTTPError(
                400, 'Malformed POST request data: {0}'.format(errmsg))

        # Successful POST request
        return 'TODO: add node [{0}]'.format(data['name'])

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_node(self, name): \
            # pylint: disable=no-self-use
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
    def delete_node(self, name): \
            # pylint: disable=unused-argument,no-self-use
        """
        Handler for /nodes/<name> (DELETE)
        """

        # TODO: handle DELETE here

        # Empty response (http status 204) for successful DELETE request
        cherrypy.response.status = 204

        return ''


def jsonify_error(status, message, traceback, version): \
        # pylint: disable=unused-argument

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


def validate_password(realm, username, password): \
        # pylint: disable=unused-argument
    """
    Simple password validation
    """
    return username in USERS and USERS[username] == password


if __name__ == '__main__':
    cherrypy_cors.install()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # /nodes (GET)
    dispatcher.connect(name='nodes',
                       route='/nodes',
                       action='get_all',
                       controller=NodesController(),
                       conditions={'method': ['GET']})

    # /nodes/{name} (GET)
    #
    # Request "/nodes/notfound" (GET) to test the 404 (not found) handler
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='get',
                       controller=NodesController(),
                       conditions={'method': ['GET']})

    # /nodes/{name} (POST)
    dispatcher.connect(name='nodes',
                       route='/nodes',
                       action='add_node',
                       controller=NodesController(),
                       conditions={'method': ['POST']})

    # /nodes/{name} (PUT)
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='update_node',
                       controller=NodesController(),
                       conditions={'method': ['PUT']})

    # /nodes/{name} (DELETE)
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='delete_node',
                       controller=NodesController(),
                       conditions={'method': ['DELETE']})

    config = {
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
        # 'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    })

    cherrypy.engine.start()
    #cherrypy.engine.block()
