# -*- coding: utf-8 -*-
"""Unit tests for Flask-Logging-Extras
"""

import logging
from logging.config import dictConfig
import sys
from unittest import TestCase

from flask import Flask, Blueprint, current_app

import flask_logging_extras


class ListHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super(ListHandler, self).__init__(*args, **kwargs)

        self.logs = []

    def emit(self, record):
        try:
            msg = self.format(record)
        except (KeyError, IndexError) as exc:
            msg = (exc.__class__.__name__, str(exc))

        self.logs.append(msg)


def configure_loggers(extra_var):
    dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'selftest': {
                'class': 'flask_logging_extras.FlaskExtraLoggerFormatter',
                'format': '%(message)s %({extra_var})s'.format(extra_var=extra_var),
            },
        },
        'handlers': {
            'selftest': {
                'class': 'test_logger_keywords.ListHandler',
                'formatter': 'selftest',
            },
        },
        'loggers': {
            'selftest': {
                'handlers': ['selftest'],
                'level': 'INFO',
            },
        },
    })

    formatter = flask_logging_extras.FlaskExtraLoggerFormatter(
        fmt='%(message)s %({extra_var})s'.format(extra_var=extra_var))

    logger = logging.getLogger('selftest')
    handlers = [handler for handler in logger.handlers if isinstance(handler, ListHandler)]
    handler = handlers[0]
    # TODO: Why doesn’t this happen automatically in Python 2.7?
    handler.setFormatter(formatter)

    return logger, handler


class LoggerKeywordsTestCase(TestCase):
    def setUp(self):
        self.logger, self.handler = configure_loggers('extra_keyword')
        self.app = Flask('test_app')
        self.app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = {
            'extra_keyword': 'placeholder',
        }

        # Make sure we don’t try to log the current blueprint for this test case
        self.app.config['FLASK_LOGGING_EXTRAS_BLUEPRINT'] = (None, '', '')

    def test_keywords_no_app_ctx(self):
        """With the current formatter, the last log line must be a just the message
        """

        self.logger.info('message')
        self.assertIn(('KeyError', "'extra_keyword'"), self.handler.logs)

    def test_keywords_app_ctx_assign_value(self):
        """If we don’t register 'extra_keyword' in the app config, we get a
        # KeyError.  We set logging.raiseExceptions to False here; the
        # reason is that this doesn’t mean an actual exception is raised,
        # but our TestingStreamHandler does that for us (which we need for
        # testing purposes)
        """

        with self.app.app_context():
            self.logger.info('message', extra=dict(extra_keyword='test'))

        self.assertIn('message test', self.handler.logs)

    def test_keywords_app_ctx_no_value(self):
        """If we don’t provide a value for a registered extra keyword, the
        # string "<unset>" will be assigned.
        """

        with self.app.app_context():
            self.logger.info('message')

        self.assertIn('message placeholder', self.handler.logs)


class LoggerBlueprintTestCase(TestCase):
    def setUp(self):
        # Register our logger class

        app = Flask('test_app')
        self.app = app
        app.config['FLASK_LOGGING_EXTRAS_BLUEPRINT'] = ('bp', '<app>', '<norequest>')

        configure_loggers('bp')
        self.logger = logging.getLogger('selftest')
        handlers = [handler for handler in self.logger.handlers if isinstance(handler, ListHandler)]
        self.handler = handlers[0]

        bp = Blueprint('test_blueprint', 'test_bp')

        @app.route('/app')
        def route_1():
            self.logger.info('Message')

            return ''

        @bp.route('/blueprint')
        def route_2():
            self.logger.info('Message')

            return ''

        app.register_blueprint(bp)

        self.client = app.test_client()

    def test_blueprint_log_no_blueprint(self):
        self.client.get('/app')
        self.assertIn('Message <app>', self.handler.logs)

    def test_blueprint_log_blueprint(self):
        self.client.get('/blueprint')
        self.assertIn('Message test_blueprint', self.handler.logs)

    def test_blueprint_log_no_request(self):
        with self.app.app_context():
            self.logger.info('Message')

        self.assertIn('Message <norequest>', self.handler.logs)
