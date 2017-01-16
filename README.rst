Flask-Logging-Extras
====================

[travis button] [coveralls button] [pypi button] [documentation button]

Flask-Logging-Extras adds additional logging features for Flask applications.

The only feature implemented now is adding extra arguments to the format
string, like this:

.. code-block:: python

   fmt = '[%(asctime)s] [%(levelname)s] [%(category)s] %(message'
   # Initialize log handlers as usual, like creating a FileHandler, and
   # assign fmt to it as a format string

   current_app.logger.info('this is the message, as usual',
                           category='fancy-category')

### Installation

pip will be available (hopefully) soon.

If you prefer to install from source, you can clone this repo and run

.. code-block:: sh

   $ python setup.py install

Usage
-----

[View the documentation online] (http://flask-jwt-extended.readthedocs.io/en/latest/)


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

You can generate a local copy of the documentation.  First, make sure you have
the flask sphinx theme available.  You can get it with

.. code-block:: sh
   $ pip install Flask-Sphinx-Themes

Then in the `docs/` directory, run

.. code-block:: sh
   $ make clean && make html

License
-------

This module is available under the BSD license.
