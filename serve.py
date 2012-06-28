import os
import sys
import time
import shutil
import urllib
import appdirs
import argparse
import tempfile
import settings
import subprocess

from zipfile import ZipFile
from multiprocessing import freeze_support, Process
from StringIO import StringIO
from cherrypy import wsgiserver
from win32api import LoadResource
from django.core.handlers.wsgi import WSGIHandler

parser = argparse.ArgumentParser(description='Emmaus House Food Pantry')
parser.add_argument('-p', '--package', help='Package file with app.')

def create_pantry_dir():
    """Create the food pantry directory to which we'll unpack."""
    temp_dir = tempfile.mkdtemp(prefix='tmp_', suffix='_food_pantry')
    food_pantry_dir = os.path.join(temp_dir, 'food_pantry')
    os.mkdir(food_pantry_dir)
    return (temp_dir, food_pantry_dir)

def unpack_pantry_data(food_pantry_dir):
    """Unpack the food pantry files to the temporary directory."""
    if args.package:
        food_pantry_zip = ZipFile(args.package)
    else:
        food_pantry_zip_data = LoadResource(0, u'FOOD_PANTRY_DATA', 1)
        food_pantry_zip = ZipFile(StringIO(food_pantry_zip_data))
    food_pantry_zip.extractall(food_pantry_dir)

def install_pantry_db(food_pantry_dir):
    """Install the db file if it isn't already there."""
    if not os.path.exists(settings.DB_FILE_DIR):
        os.makedirs(settings.DB_FILE_DIR)

    temp_db_file = os.path.join(food_pantry_dir, settings.DB_FILE_NAME)
    if os.path.exists(settings.DB_FILE_PATH):
        os.remove(temp_db_file)
    else:
        os.rename(temp_db_file, settings.DB_FILE_PATH)

def start_chrome():
    chrome_dir = appdirs.user_data_dir('Chrome', 'Google')
    subprocess.call([os.path.join(chrome_dir, 'Application', 'chrome.exe'),
                     '--app=http://localhost:8080'])

def start_server(temp_dir):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'food_pantry.settings'
    sys.path.append(temp_dir)
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), WSGIHandler())
    try:
        # Beware: If you start the server from the command line then it will
        # catch the CTRL-c command.
        server.start()
    except KeyboardInterrupt:
        server.stop()
    delete_temp_dir(temp_dir)

def delete_temp_dir(temp_dir):
    """Delete the temporary directory."""
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    freeze_support()
    args = parser.parse_args()

    # Try to connect to the server and verify the version. If it fails to
    # connect, start it. If the version info is wrong, signal an error.

    try:
        version_page = urllib.urlopen('http://localhost:8080/version')
        version = version_page.read()
        if version != settings.VERSION:
            # Signal some kind of error. If the version of the server is
            # old we should probably kill and restart the server.
            pass
    except IOError as ioe:
        temp_dir, food_pantry_dir = create_pantry_dir()
        unpack_pantry_data(food_pantry_dir)
        install_pantry_db(food_pantry_dir)

        process = Process(target=start_server, args=(temp_dir,))
        process.start()
        time.sleep(1)

    start_chrome()

    # Beware: this will exit without calling cleanup handlers, flushing
    # stdio buffers, etc. This implements a poor-man's fork(). We use the
    # multiprocessing module to launch the server and then exit the
    # parent process.
    os._exit(0)
else:
    class DummyArgs:
        def __getattr__(self, field):
            return None
    args = DummyArgs()
