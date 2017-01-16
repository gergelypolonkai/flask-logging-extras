Flask-Logging-Extras
====================

.. image:: https://travis-ci.org/gergelypolonkai/flask-logging-extras.svg?branch=master
    :target: https://travis-ci.org/gergelypolonkai/flask-logging-extras

.. image:: https://codecov.io/gh/gergelypolonkai/flask-logging-extras/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/gergelypolonkai/flask-logging-extras

.. image:: https://badge.fury.io/py/Flask-Logging-Extras.svg
    :target: https://badge.fury.io/py/Flask-Logging-Extras

.. image:: https://readthedocs.org/projects/flask-logging-extras/badge/?version=latest
    :target: http://flask-logging-extras.readthedocs.io/en/latest/?badge=latest

Flask-Logging-Extras adds additional logging features for Flask applications.

The only feature implemented now is adding extra arguments to the format
string, like this (this example adds the category keyword to the logs:

.. code-block:: python

   fmt = '[%(asctime)s] [%(levelname)s] [%(category)s] %(message'
   # Initialize log handlers as usual, like creating a FileHandler, and
   # assign fmt to it as a format string
   app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = {'category': '<unset>'}
   app.logger.init_app(app)

   current_app.logger.info('this is the message, as usual',
                           category='fancy-category')

Installation
------------

The easiest way to start using the package is with pip:

.. code-block:: sh

   $ pip install Flask-Logging-Extras

If you prefer to install from source, you can clone this repo and run

.. code-block:: sh

   $ python setup.py install

Usage
-----

`View the documentation online
<http://flask-logging-extras.readthedocs.io/>`_

Testing and Code Coverage
-------------------------

We require 100% code coverage in our unit tests. We run all the unit tests
with tox, which will test against python2.7, 3.3, 3.4, and 3.5.

Running tox will print out a code coverage report.  Coverage report is also
available on codecov.

tox is running automatically for every push in Travis-CI.  To run tox on
your local machine, you can simply invoke it with the `tox` command.

Generating Documentation
------------------------

You can generate a local copy of the documentation.  First, make sure you
have the flask sphinx theme available.  You can get it (and all possible
documentation requirements) with

.. code-block:: sh

   $ pip install -r docs-requirements.txt

Then in the `docs/` directory, run

.. code-block:: sh

   $ make clean && make html

License
-------

This module is available under the BSD license.
