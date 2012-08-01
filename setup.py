import os
import sys
import shutil
import py2exe
import argparse
import subprocess
import compileall
from distutils.core import setup
from zipfile import ZipFile

parser = argparse.ArgumentParser(description='Emmaus House Food Pantry Setup')
parser.add_argument('-c', '--clean', action='store_true',
                    default=False, help='Clean all built files.')
parser.add_argument('-p', '--pack', action='store_true',
                    default=False, help='Pack app files into archive.')
parser.add_argument('-b', '--build', action='store_true',
                    default=False, help='Build executable.')

def clean():
    if os.path.exists('./food_pantry.zip'):
        print 'Removing archive: ./food_pantry.zip ...'
        os.remove('./food_pantry.zip')

    if os.path.exists('./build'):
        print 'Removing directory: ./build ...'
        shutil.rmtree('./build')

    if os.path.exists('./dist'):
        print 'Removing directory: ./dist ...'
        shutil.rmtree('./dist')

def pack():
    if os.path.exists('./pantry.db'):
        print 'Removing previous database: ./pantry.db ...'
        os.remove('./pantry.db')
    print 'Creating new database ...'
    subprocess.check_call('python.exe manage.py syncdb --noinput')
    print 'Loading data in new database ...'
    subprocess.check_call('python.exe manage.py loaddata data\\initial_v2.json')

    print 'Compiling python files ...'
    compileall.compile_dir('.', force=True)

    print 'Composing list of files for archive ...'
    files = []
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    print 'Creating archive file ...'
    with ZipFile('food_pantry.zip', 'w') as food_pantry_zip:
        for filename in files:
            food_pantry_zip.write(filename)

def build():
    print 'Reading archive into memory ...'
    with open('./food_pantry.zip', 'rb') as food_pantry_zip:
        food_pantry_data = food_pantry_zip.read()

    print 'Invoking py2exe to generate the executable ...'
    excludes = ['pywin', 'pywin.debugger', 'pywin.debugger.dbgcon',
                'pywin.dialogs', 'pywin.dialogs.list', 'Tkconstants',
                'Tkinter', 'tcl', 'zmq', 'Pythonwin', 'IPython', 'MySQLdb',
                'PIL', 'matplotlib', 'nose', 'numpy', 'pyreadline', 'scipy',
                'win32', 'win32com']

    sys.argv[1:] = ['py2exe']
    setup(windows=[{'script': 'webapp.py',
                    'other_resources':
                        [(u'FOOD_PANTRY_DATA', 1, food_pantry_data)]}],
          options = {'py2exe': {'bundle_files': 1,
                                'dll_excludes': ['w9xpopen.exe', 'MSVCP90.dll',
                                                 'mswsock.dll', 'powrprof.dll'],
                                'excludes': excludes,
                                'packages': ['django', 'email', 'win32api',
                                             'cherrypy', 'appdirs']}},
          zipfile = None)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.clean: clean()
    if args.pack: pack()
    if args.build: build()
else:
    class DummyArgs:
        def __getattr__(self, field):
            return None
    args = DummyArgs()
