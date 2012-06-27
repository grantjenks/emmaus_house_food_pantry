import os
import sys
import time
import shutil
import appdirs
import tempfile
import settings
import subprocess

from zipfile import ZipFile
from threading import Thread
from StringIO import StringIO
from cherrypy import wsgiserver
from win32api import LoadResource
from django.core.handlers.wsgi import WSGIHandler

print 'Starting server ...'

# Create the food pantry directory to which we'll unpack.

temp_dir = tempfile.mkdtemp(prefix='tmp_', suffix='_food_pantry')
food_pantry_dir = os.path.join(temp_dir, 'food_pantry')
os.mkdir(food_pantry_dir)

# Unpack the food pantry files to the temporary directory.

food_pantry_zip = ZipFile(StringIO(LoadResource(0, u'FOOD_PANTRY_DATA', 1)))
food_pantry_zip.extractall(food_pantry_dir)

# Install the db file if it isn't already there.

if not os.path.exists(settings.DB_FILE_DIR):
    os.makedirs(settings.DB_FILE_DIR)

temp_db_file = os.path.join(food_pantry_dir, settings.DB_FILE_NAME)
if os.path.exists(settings.DB_FILE_PATH):
    os.remove(temp_db_file)
else:
    os.rename(temp_db_file, settings.DB_FILE_PATH)

# Setup the environment for django.

os.environ['DJANGO_SETTINGS_MODULE'] = 'food_pantry.settings'
sys.path.append(temp_dir)

def start_chrome():
    time.sleep(1)
    chrome_dir = appdirs.user_data_dir('Chrome', 'Google')
    subprocess.call([os.path.join(chrome_dir, 'Application', 'chrome.exe'),
                     '--app=http://localhost:8080'])

# Run the server.

server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), WSGIHandler())
try:
    thread = Thread(target=start_chrome)
    thread.start()
    print 'Press CTRL-c to stop the server.'
    server.start()
except KeyboardInterrupt:
    server.stop()
    thread.join()

# Delete the temporary directory.

shutil.rmtree(temp_dir)
