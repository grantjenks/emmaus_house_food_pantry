import settings as pantry_settings
from django.conf import global_settings, settings

for setting in dir(pantry_settings):
    if setting == setting.upper():
        value = getattr(pantry_settings, setting)
        setattr(global_settings, setting, value)

settings.configure(global_settings)

from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import AdminMediaHandler, run, WSGIServerException

run('', 8080, WSGIHandler())

"""
import os
import sys
from django.core.handlers.wsgi import WSGIHandler
from cherrypy import wsgiserver

os.environ['DJANGO_SETTINGS_MODULE'] = 'food_pantry.settings'

sys.path.append('c:/Users/Grant/repos/fun/')

server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), WSGIHandler())

try:
    server.start()
except KeyboardInterrupt:
    server.stop()
"""
