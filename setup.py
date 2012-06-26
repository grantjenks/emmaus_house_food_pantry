from distutils.core import setup
import py2exe

excludes = ['pywin', 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs',
            'pywin.dialogs.list', 'Tkconstants', 'Tkinter', 'tcl', 'zmq',
            'Pythonwin', 'IPython', 'MySQLdb', 'PIL', 'matplotlib', 'nose',
            'numpy', 'pyreadline', 'scipy', 'win32', 'win32com']


setup(console=['serve.py'],
      options = {'py2exe': {'bundle_files': 1,
                            'dll_excludes': ['w9xpopen.exe', 'MSVCP90.dll'],
                            'excludes': excludes,
                            'packages': ['django', 'email']}},
      zipfile = None)
