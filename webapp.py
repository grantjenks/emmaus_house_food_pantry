"""
Management utilities for deploying django site as web application.
"""

import settings
import os

PORT = 35124
BASE_URL = 'http://localhost:{}'.format(PORT)

def create_pantry_dir():
    """Create an empty food pantry directory to which we'll unpack."""
    import shutil
    temp_dir = os.path.join(settings.APPDIRS.user_cache_dir, 'modules')
    food_pantry_dir = os.path.join(temp_dir, 'emmaus_house_food_pantry')
    if os.path.exists(temp_dir):
        log.info('Deleting food pantry cache dir')
        shutil.rmtree(temp_dir)
    log.info('Creating food pantry cache dir at {}'.format(food_pantry_dir))
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
    log.info('Extracting zip file data to food pantry cache dir')
    food_pantry_zip.extractall(food_pantry_dir)

def install_pantry_db(temp_dir, food_pantry_dir):
    """Install the db file if it isn't already there."""
    if not os.path.exists(settings.DB_FILE_DIR):
        os.makedirs(settings.DB_FILE_DIR)
    temp_db_file = os.path.join(food_pantry_dir, settings.DB_FILE_NAME)
    if os.path.exists(settings.DB_FILE_PATH):
        log.info('Database already installed; deleting unpacked file')
        os.remove(temp_db_file)
    else:
        from appdirs import AppDirs
        v1_appdirs = AppDirs('FoodPantry', 'GrantJenks', version='1.0')
        v1_db_file = os.path.join(v1_appdirs.user_data_dir, 'pantry.db')
        if os.path.exists(v1_db_file):
            log.info('Upgrading database from v1 to v2')
            log.info('Copying database from v1 to v2 directory')
            import shutil
            shutil.copyfile(v1_db_file, settings.DB_FILE_PATH)
            migrate_v1_v2(temp_dir, food_pantry_dir)
        else:
            log.info('Installing database file via rename')
            os.rename(temp_db_file, settings.DB_FILE_PATH)

def migrate_v1_v2(temp_dir, food_pantry_dir):
    import sys

    os.environ['DJANGO_SETTINGS_MODULE'] = 'emmaus_house_food_pantry.settings'
    sys.path.append(temp_dir)
    sys.path.append(food_pantry_dir)

    from django.db import connection

    # Alter tables for rename.

    cursor = connection.cursor()
    renames = [('food_pantry_category', 'core_category'),
               ('food_pantry_item', 'core_item'),
               ('food_pantry_label', 'core_label'),
               ('food_pantry_subcategory', 'core_subcategory')]
    for rename in renames:
        cursor.execute('alter table {} rename to {}'.format(*rename))

    # Add new tables.

    cursor.execute("""
        CREATE TABLE "core_bagcount" (
            "id" integer NOT NULL PRIMARY KEY,
            "category_id" integer NOT NULL UNIQUE REFERENCES "core_category" ("id"),
            "count" integer NOT NULL
        );""")
    cursor.execute("""
        CREATE TABLE "core_setting" (
            "id" integer NOT NULL PRIMARY KEY,
            "key" varchar(64) NOT NULL UNIQUE,
            "value" varchar(512)
        );""")

    cursor.close()
    connection.close()

    # Load data into new tables.
    # This is trickier than it should be. Normally, it would look like:
    #     from django.core.management import call_command
    #     call_command('loaddata', 'data/migrate_v1_v2.json', verbosity=0)
    # but that logic assumes the use of __path__ which we don't have when
    # packaged as a program.
    # See django/core/management/base.py for details on the code that is
    # mimicked here.

    from django.core.management.commands import loaddata
    from optparse import NO_DEFAULT
    command = loaddata.Command()
    defaults = dict([(opt.dest, opt.default)
                     for opt in command.option_list
                     if opt.default is not NO_DEFAULT])
    defaults.update({'verbosity':'0'})
    migrate_file = os.path.join(food_pantry_dir, 'data', 'migrate_v1_v2.json')
    command.execute(migrate_file, **defaults)

def start_chrome():
    """Start Google Chrome web browser."""
    import appdirs
    import subprocess

    browsers = []

    chrome_dir = appdirs.user_data_dir('Chrome', 'Google')
    chrome_exe = os.path.join(chrome_dir, 'Application', 'chrome.exe')
    browsers.append(['start', '""', chrome_exe, '--app={}'.format(BASE_URL)])

    chrome_exe = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
    browsers.append(['start', '""', chrome_exe, '--app={}'.format(BASE_URL)])

    for browser in browsers:
        if os.path.exists(browser[2].strip('"')):
            log.info('Launching browser at {}'.format(browser[2]))
            log.info('Using command: {}'.format(' '.join(browser)))
            subprocess.call(' '.join(browser), shell=True)
            break
    else:
        msg = 'No browser found to launch! Navigate to {}'.format(BASE_URL)
        log.error(msg)

def start_server(temp_dir, food_pantry_dir):
    """Start CherryPy WSGI webserver."""
    import sys
    from cherrypy import wsgiserver
    from django.core.handlers.wsgi import WSGIHandler
    os.environ['DJANGO_SETTINGS_MODULE'] = 'emmaus_house_food_pantry.settings'
    sys.path.append(temp_dir)
    sys.path.append(food_pantry_dir)
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', PORT), WSGIHandler())
    try:
        # Beware: If you start the server from the command line then it will
        # catch the CTRL-c command.
        log.info('Starting webserver on localhost:{}'.format(PORT))
        server.start()
    except KeyboardInterrupt:
        server.stop()

# Configure arguments parsing.

import argparse
parser = argparse.ArgumentParser(description='Emmaus House Food Pantry')
parser.add_argument('-p', '--package', help='Package file with app.')

# Global 'log' is used by the utility functions to document behavior.
# When imported, the NullHandler is used to suppress output.

import logging
log = logging.getLogger('emmaus_house_food_pantry.webapp')

# Create the webapp log, data, and cache directories if they don't
# already exist.

def make_if_dne(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
make_if_dne(settings.APPDIRS.user_log_dir)
make_if_dne(settings.APPDIRS.user_data_dir)
make_if_dne(settings.APPDIRS.user_cache_dir)

if __name__ == '__main__':
    import time
    import urllib
    from multiprocessing import freeze_support, Process
    freeze_support()
    args = parser.parse_args()

    # Configure logging to file.

    logpath = os.path.join(settings.APPDIRS.user_log_dir, 'webapp.log')
    handler = logging.FileHandler(logpath)
    formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    # If we can connect to the server and verify the version, then just
    # start Chrome. Otherwise, unpack and start the server.

    do_start_server = False

    try:
        version_page = urllib.urlopen('{}/pantry/version'.format(BASE_URL))
        version = version_page.read()
        if version != settings.VERSION:
            log.warning('Version mismatch! {} != {}'.format(version,
                                                            settings.VERSION))
            shutdown_url = '{}/pantry/shutdown'.format(BASE_URL)
            shutdown_page = urllib.urlopen(shutdown_url)
            shutdown_msg = shutdown_page.read()
            time.sleep(3)
            do_start_server = True
    except IOError:
        do_start_server = True

    if do_start_server:
        temp_dir, food_pantry_dir = create_pantry_dir()
        unpack_pantry_data(food_pantry_dir)
        install_pantry_db(temp_dir, food_pantry_dir)

        dirs = (temp_dir, food_pantry_dir)
        process = Process(target=start_server, args=dirs)
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
    log.addHandler(logging.NullHandler())
