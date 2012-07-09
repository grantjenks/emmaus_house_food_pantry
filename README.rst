Emmaus House Food Pantry Inventory Management
=============================================

Food Pantry inventory management program for Emmaus House Episcopal Church.

Designed for use with modern USB barcode scanners.

Installation
------------

Simply download the program to your desktop and double-click.

`Click here <https://github.com/downloads/grantjenks/emmaus_house_food_pantry/pantry.exe>`_ to download the latest version of the program.

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
