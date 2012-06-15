import os
import sys
from django.core.handlers.wsgi import WSGIHandler
from cherrypy import wsgiserver

os.environ['DJANGO_SETTINGS_MODULE'] = 'food_pantry.settings'

sys.path.append('c:/Users/Grant/repos/fun/')

server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), WSGIHandler())
server.start()
