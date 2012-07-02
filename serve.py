import os
import settings
import argparse

parser = argparse.ArgumentParser(description='Emmaus House Food Pantry')
parser.add_argument('-p', '--package', help='Package file with app.')

def create_pantry_dir():
    """Create an empty food pantry directory to which we'll unpack."""
    import shutil
    temp_dir = os.path.join(settings.APPDIRS.user_cache_dir, 'modules')
    food_pantry_dir = os.path.join(temp_dir, 'food_pantry')
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(food_pantry_dir)
    return (temp_dir, food_pantry_dir)

def unpack_pantry_data(food_pantry_dir):
    """Unpack the food pantry files to the temporary directory."""
    from StringIO import StringIO
    from win32api import LoadResource
    from zipfile import ZipFile
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
    import appdirs
    import subprocess
    chrome_dir = appdirs.user_data_dir('Chrome', 'Google')
    chrome_exe = os.path.join(chrome_dir, 'Application', 'chrome.exe')
    subprocess.call(['start', chrome_exe, '--app=http://localhost:514143'],
                    shell=True)

def start_server(temp_dir):
    import sys
    from cherrypy import wsgiserver
    from django.core.handlers.wsgi import WSGIHandler
    os.environ['DJANGO_SETTINGS_MODULE'] = 'food_pantry.settings'
    sys.path.append(temp_dir)
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 514143), WSGIHandler())
    try:
        # Beware: If you start the server from the command line then it will
        # catch the CTRL-c command.
        server.start()
    except KeyboardInterrupt:
        server.stop()

if __name__ == '__main__':
    import time
    import urllib
    from multiprocessing import freeze_support, Process
    freeze_support()
    args = parser.parse_args()

    # If we can connect to the server and verify the version, then just
    # start Chrome. Otherwise, unpack and start the server.

    do_start_server = False

    try:
        version_page = urllib.urlopen('http://localhost:514143/version')
        version = version_page.read()
        if version != settings.VERSION:
            shutdown_page = urllib.urlopen('http://localhost:514143/shutdown')
            shutdown_msg = shutdown_page.read()
            time.sleep(3)
            do_start_server = True
    except IOError:
        do_start_server = True

    if do_start_server:
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
    if do_start_server: os._exit(0)
else:
    class DummyArgs:
        def __getattr__(self, field):
            return None
    args = DummyArgs()
