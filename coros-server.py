import cherrypy


config = {
  'global' : {
    'server.socket_host' : '127.0.0.1',
    'server.socket_port' : 8080,
    'server.thread_pool' : 8,
  }
}


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


class App:

  @cherrypy.expose
  def index(self):
    return '''<!DOCTYPE html>
      <html>
      <head>
      <meta content='text/html; charset=utf-8' http-equiv='content-type'>
      <title>CORS AJAX JSON request</title>
      <script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js'></script>
      <script type='text/javascript'>
        $(document).ready(function()
        {
          $('button').on('click', function()
          {
            $.ajax({
              'type'        : 'POST',
              'dataType'    : 'JSON',
              'contentType' : 'application/json',
              'url'         : 'http://proxy:8080/endpoint',
              'data'        : JSON.stringify({'foo': 'bar'}),
              'success'     : function(response)
              {
                console.log(response);  
              }
            });
          })
        });
      </script>
      </head>
      <body>
        <button>make request</button>
      </body>
      </html>
    '''

  @cherrypy.expose
  #@cherrypy.config(**{'tools.cors.on': True})
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def endpoint(self):
    data = cherrypy.request.json
    return data


if __name__ == '__main__':
  cherrypy.config.update({
    'tools.cors.on': True
  })
  cherrypy.quickstart(App(), '/', config)
