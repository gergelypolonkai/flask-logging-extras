# -*- coding: utf-8 -*-
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Extra functionality for Flask logging

Flask-Logging-Extras is a Flask extension that plugs into the logging
mechanism of Flask applications.

Flask-Logging-Extras requires you to set FLASK_LOGGING_EXTRAS_KEYWORDS to a
dictionary value, where the dictionary key is a the key you can use in the
log message format, and the value is a default value that is substituted if
no value is present in the message record.
"""

from importlib import import_module
import logging

from flask import has_request_context, request, current_app, has_app_context

__version_info__ = ('2', '0', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Gergely Polonkai'
__license__ = 'MIT'
__copyright__ = '(c) 2015-2018 Benchmarked.games'


def _import_by_string(fqn):
    try:
        mod_name, var_name = fqn.rsplit('.', 1)
    except ValueError:
        mod_name = fqn
        var_name = None

    mod = import_module(mod_name)

    if var_name is None:
        return mod

    try:
        var = getattr(mod, var_name)
    except AttributeError:
        raise ImportError('{var_name} not found in {mod_name}'.format(var_name=var_name, mod_name=mod_name))

    return var


class FlaskExtraLoggerFormatter(logging.Formatter):
    """A log formatter class that is capable of adding extra keywords to log
    formatters and logging the blueprint name

    Usage:

    .. code-block:: python

       import logging
       from logging.config import dictConfig

       dictConfig({
           'formatters': {
               'extras': {
                   'format': '[%(asctime)s] [%(levelname)s] [%(category)s] [%(bp)s] %(message)s',
               },
           },
           'handlers': {
               'extras_handler': {
                   'class': 'logging.FileHandler',
                   'args': ('app.log', 'a'),
                   'formatter': 'extras',
                   'level': 'INFO',
               },
           },
           'loggers': {
               'my_app': {
                   'handlers': ['extras_handler'],
               }
           },
       })

       app = Flask(__name__)
       app.config['FLASK_LOGGING_EXTRAS'] = {
           'BLUEPRINT': {
               'FORMAT_NAME': 'bp',
               'APP_BLUEPRINT': '<app>',
               'NO_REQUEST_BLUEPRINT': '<not a request>',
           },
           'RESOLVERS': {
               'categoy': '<unset>',
               'client': 'log_helper.get_client',
           },
       }

       bp = Blueprint('my_blueprint', __name__)
       app.register_blueprint(bp)

       logger = logging.getLogger('my_app')

       # This will produce something like this in app.log:
       # [2018-05-02 12:44:48.944] [INFO] [my category] [<not request>] The message
       logger.info('The message', extra=dict(category='my category'))

       # This will produce something like this in app.log:
       # [2018-05-02 12:44:48.944] [INFO] [None] [<not request>] The message
       logger.info('The message')

       @app.route('/1')
       def route_1():
           # This will produce a log message like this:
           # [2018-05-02 12:44:48.944] [INFO] [<unset>] [<app>] Message
           logger.info('Message')

           return ''

       @bp.route('/2')
       def route_2():
           # This will produce a log message like this:
           # [2018-05-02 12:44:48.944] [INFO] [None] [my_blueprint] Message
           logger.info('Message')

           return ''

       # This will produce a log message like this:
       # [2018-05-02 12:44:48.944] [INFO] [<unset>] [<NOT REQUEST>] Message
       logger.info('Message')
    """

    def __init__(self, *args, **kwargs):
        super(FlaskExtraLoggerFormatter, self).__init__(*args, **kwargs)

        self.resolvers = {}
        self.bp_var = None
        self.bp_app = None
        self.bp_noreq = None
        self.__inited = False

    def init_app(self, app):
        """Initialise the formatter with app-specific values from ``app``’s configuration
        """

        if self.__inited:
            return

        config = app.config.get(
            'FLASK_LOGGING_EXTRAS', {})

        blueprint_config = config.get('BLUEPRINT', {})
        self.bp_var = blueprint_config.get('FORMAT_NAME', 'blueprint')
        self.bp_app = blueprint_config.get('APP_BLUEPRINT', '<app>')
        self.bp_noreq = blueprint_config.get('NO_REQUEST_BLUEPRINT', '<not a request>')

        for var_name, resolver_fqn in config.get('RESOLVERS', {}).items():
            if resolver_fqn is None:
                resolver = None
            else:
                try:
                    resolver = _import_by_string(resolver_fqn)
                except ImportError:
                    resolver = resolver_fqn

            self.resolvers[var_name] = resolver

            self.__inited = True

    def format(self, record):
        blueprint = None

        if has_app_context():
            self.init_app(current_app)

            if self.bp_var and has_request_context():
                blueprint = request.blueprint or self.bp_app

        if self.bp_var and self.bp_var not in record.__dict__:
            setattr(record, self.bp_var, blueprint or self.bp_noreq)

        for var_name, resolver in self.resolvers.items():
            if var_name in record.__dict__:
                continue

            setattr(record, var_name, resolver() if callable(resolver) else resolver)

        return super(FlaskExtraLoggerFormatter, self).format(record)
