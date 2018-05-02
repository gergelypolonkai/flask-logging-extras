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

import logging

from flask import has_request_context, request, current_app, has_app_context

__version_info__ = ('1', '0', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Gergely Polonkai'
__license__ = 'MIT'
__copyright__ = '(c) 2015-2018 Benchmarked.games'


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
                   'format': '[%(asctime)s] [%(levelname)s] [%(category)s] [%(blueprint)s] %(message)s',
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
       app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = {'category': '<unset>'}
       app.config['FLASK_LOGGING_EXTRAS_BLUEPRINT'] = ('blueprint',
                                                       '<APP>',
                                                       '<NOT REQUEST>')

       bp = Blueprint('my_blueprint', __name__)
       app.register_blueprint(bp)

       logger = logging.getLogger('my_app')

       # This will produce something like this in app.log:
       # [2018-05-02 12:44:48.944] [INFO] [my category] [<NOT REQUEST>] The message
       logger.info('The message', extra=dict(category='my category'))

       @app.route('/1')
       def route_1():
           # This will produce a log message like this:
           # [2018-05-02 12:44:48.944] [INFO] [<unset>] [<APP>] Message
           logger.info('Message')

           return ''

       @bp.route('/2')
       def route_2():
           # This will produce a log message like this:
           # [2018-05-02 12:44:48.944] [INFO] [<unset>] [my_blueprint] Message
           logger.info('Message')

           return ''

       # This will produce a log message like this:
       # [2018-05-02 12:44:48.944] [INFO] [<unset>] [<NOT REQUEST>] Message
       logger.info('Message')
    """

    def _collect_keywords(self, record):
        """Collect all valid keywords and add them to the log record if not present
        """

        # We assume we do have an active app context here
        defaults = current_app.config.get('FLASK_LOGGING_EXTRAS_KEYWORDS', {})

        for keyword, default in defaults.items():
            if keyword not in record.__dict__:
                setattr(record, keyword, default)

    def format(self, record):
        bp_var, bp_app, bp_noreq = ('blueprint', '<app>', '<not a request>')
        blueprint = None

        if has_app_context():
            self._collect_keywords(record)

            bp_var, bp_app, bp_noreq = current_app.config.get('FLASK_LOGGING_EXTRAS_BLUEPRINT',
                                                              (bp_var, bp_app, bp_noreq))

            if bp_var and has_request_context():
                blueprint = request.blueprint or bp_app

        if bp_var and bp_var not in record.__dict__:
            blueprint = blueprint or bp_noreq

            setattr(record, bp_var, blueprint)

        return super(FlaskExtraLoggerFormatter, self).format(record)
