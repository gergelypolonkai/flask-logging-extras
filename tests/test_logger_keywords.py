# -*- coding: utf-8 -*-
"""
Unit tests for Flask-Logging-Extras
"""

import logging
import sys
from unittest import TestCase

from flask import Flask

import flask_logging_extras

class ListStream(object):
    """
    Primitive stream that stores its input lines in a list
    """

    def __init__(self, *args, **kwargs):
        self.lines = []

        super(ListStream, self).__init__(*args, **kwargs)

    def write(self, data):
        if len(self.lines) == 0 or self.lines[-1].endswith('\n'):
            self.lines.append(data)
        else:
            self.lines[-1] += data


class TestingStreamHandler(logging.StreamHandler):
    def handleError(self, record):
        exc, exc_msg, trace = sys.exc_info()

        super(logging.StreamHandler, self).handleError(record)

        raise(exc(exc_msg))


class LoggerKeywordsTestCase(TestCase):
    def setUp(self):
        self.original_logger_class = logging.getLoggerClass()

    def tearDown(self):
        logging.setLoggerClass(self.original_logger_class)

    def test_logger_registration(self):
        class NotLoggerClass(object):
            pass

        with self.assertRaises(TypeError):
            flask_logging_extras.register_logger_class(cls=NotLoggerClass)

        original_logging_class = logging.getLoggerClass()

        old_class = flask_logging_extras.register_logger_class()

        # If no class is specified, FlaskExtraLogger should be registered
        self.assertEqual(logging.getLoggerClass(),
                         flask_logging_extras.FlaskExtraLogger)
        # The return value of this function should be the old default
        self.assertEqual(original_logging_class, old_class)

        class MyLogger(logging.Logger):
            pass

        # Calling register_logger_class() with any subclass of
        # logging.Logger should succeed
        flask_logging_extras.register_logger_class(cls=MyLogger)

    def test_logger_class(self):
        # If app is present during __init__, and is not None, we should get
        # a TypeError
        with self.assertRaises(TypeError):
            flask_logging_extras.FlaskExtraLogger('test_logger',
                                                  app='test value')

        # If app is present, but is None, no exception should be raised
        flask_logging_extras.FlaskExtraLogger('test_logger', app=None)

    def test_logger_class_init_app(self):
        logger = flask_logging_extras.FlaskExtraLogger('test')
        app = Flask('test_app')

        logger.init_app(app)

        self.assertEqual({}, logger._valid_keywords)

        app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = {'exc_info': None}

        with self.assertRaises(ValueError):
            logger.init_app(app)

        app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = {'my_keyword': '<unset>'}

        logger.init_app(app)
        self.assertEqual({'my_keyword': '<unset>'}, logger._valid_keywords)

        # Without registration first, app.logger should not be of class
        # FlaskExtraLogger (even though logger.init_app() succeeded without
        # it.)
        self.assertNotIsInstance(app.logger,
                                 flask_logging_extras.FlaskExtraLogger)

        flask_logging_extras.register_logger_class()

        # Even after registratiiion, existing apps are (obviously) not
        # tampered with

        self.assertNotIsInstance(app.logger,
                                 flask_logging_extras.FlaskExtraLogger)

        app = Flask('test_app')

        # Newly created apps, though, should be made with this class
        self.assertIsInstance(app.logger,
                              flask_logging_extras.FlaskExtraLogger)

    def _create_app_with_logger(self, fmt, keywords=[]):
        app = Flask('test_app')

        self.assertIsInstance(app.logger,
                              flask_logging_extras.FlaskExtraLogger)

        app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = keywords
        app.logger.init_app(app)

        formatter = logging.Formatter(fmt)
        stream = ListStream()

        handler = TestingStreamHandler(stream=stream)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)

        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)

        return app, stream

    def test_keywords(self):
        # Register our logger class as the default
        old_logger_class = flask_logging_extras.register_logger_class()

        app, log_stream = self._create_app_with_logger('%(message)s')

        app.logger.info('message')
        # With the current formatter, the last log line must be a just the
        # message
        self.assertEqual(log_stream.lines[-1], 'message\n')

        app, log_stream = self._create_app_with_logger(
            '%(message)s %(extra_keyword)s')

        # If we don’t register 'extra_keyword' in the app config, we get a
        # KeyError.  We set logging.raiseExceptions to False here; the
        # reason is that this doesn’t mean an actual exception is raised,
        # but our TestingStreamHandler does that for us (which we need for
        # testing purposes)
        old_raiseExceptions = logging.raiseExceptions
        logging.raiseExceptions = False
        with self.assertRaises(KeyError):
            app.logger.info('message')
        logging.raiseExceptions = old_raiseExceptions

        app, log_stream = self._create_app_with_logger(
            '%(message)s [%(extra_keyword)s]',
            keywords={'extra_keyword': '<unset>'})

        app.logger.info('message', extra_keyword='test')
        self.assertEqual('message [test]\n', log_stream.lines[-1])

        # If we don’t provide a value for a registered extra keyword, the
        # string "<unset>" will be assigned.
        app.logger.info('message')
        self.assertEqual('message [<unset>]\n', log_stream.lines[-1])
