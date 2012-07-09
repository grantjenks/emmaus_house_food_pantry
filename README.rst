Emmaus House Food Pantry Inventory Management
=============================================

Food Pantry inventory management program for Emmaus House Episcopal Church.

Designed for use with modern USB barcode scanners.

Installation
------------

Simply download the program to your desktop and double-click.

Development
-----------

Building
........

::

    python setup.py --help
    usage: setup.py [-h] [-c] [-p] [-b]
    
    Emmaus House Food Pantry Setup
    
    optional arguments:
      -h, --help   show this help message and exit
      -c, --clean  Clean all built files.
      -p, --pack   Pack app files into archive.
      -b, --build  Build executable.

Webapp Testing
..............

::

    python webapp.py --package food_pantry.zip
