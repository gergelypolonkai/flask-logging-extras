"""
Extra functionality for Flask logging

Flask-Logging-Extras is a Flask extension that plugs into the logging
mechanism of Flask applications.
"""

import logging

__version_info__ = ('0', '0', '1')
__version__ = '.'.join(__version_info__)
__author__ = 'Gergely Polonkai'
__license__ = 'BSD'
__copyright__ = '(c) 2015 GT2'

class FlaskExtraLogger(logging.getLoggerClass()):
    """
    A logger class that is capable of adding extra keywords to log formatters
    """

    def __init__(self, *args, **kwargs):
        if 'app' in kwargs and kwargs['app'] is not None:
            raise TypeError(
                "Cannot initialise {classname} with an app.  "
                "See the documentation of Flask-Logging-Extras for more info."
                .format(classname=self.__class__.__name__))

        super(FlaskExtraLogger, self).__init__(*args, **kwargs)

    def _log(self, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        for kw in self._valid_keywords:
            if kw in kwargs:
                kwargs['extra'][kw] = kwargs[kw]

        super(FlaskExtraLogger, self)._log(*args, **kwargs)

    def init_app(self, app):
        self.app = app

        self.app.config.setdefault('FLASK_LOGGING_EXTRAS_KEYWORDS', [])

        for kw in self.app.config['FLASK_LOGGING_EXTRAS_KEYWORDS']:
            if kw in ['exc_info', 'extra', 'stack_info']:
                raise ValueError(
                    '"{keyword}" member of FLASK_LOGGING_EXTRAS_KEYWORDS is '
                    'reserved for internal use.')


def register_logger_class(cls=FlaskExtraLogger):
    """
    Register a new logger class

    It is effectively a wrapper around logging.setLoggerClass(), with an
    added check to make sure the class can be used as a logger.

    To use the extra features of the logger class in a Flask app, you must
    call it before the app is instantiated.
    """

    if not issubclass(cls, logging.Logger):
        raise TypeError(
            "The logger class must be a subclass of logging.Logger!")

    logging.setLoggerClass(cls)
