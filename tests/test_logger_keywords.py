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
        self.app.config['FLASK_LOGGING_EXTRAS'] = {
            'BLUEPRINT': {
                'FORMAT_NAME': None,
                'APP_BLUEPRINT': '',
                'NO_REQUEST_BLUEPRINT': '',
            },
            'RESOLVERS': {
                'extra_keyword': 'placeholder',
            },
        }

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
            self.logger.info('message', extra=dict(extra_keyword='first'))
            self.logger.info('message', extra=dict(extra_keyword='second'))

        self.assertIn('message first', self.handler.logs)
        self.assertIn('message second', self.handler.logs)

    def test_keywords_app_ctx_no_value(self):
        """If we don’t provide a value for a registered extra keyword, the
        # string "<unset>" will be assigned.
        """

        with self.app.app_context():
            self.logger.info('message')

        self.assertIn('message placeholder', self.handler.logs)

    def test_resolver_simple_importable(self):
        """Test if the resolver is an importable module
        """

        self.app.config['FLASK_LOGGING_EXTRAS']['RESOLVERS'] = {
            'extra_keyword': 'flask_logging_extras',
        }

        with self.app.app_context():
            self.logger.info('message')

        log = self.handler.logs[0]
        self.assertTrue(log.startswith('message <module \'flask_logging_extras\' from '))

    def test_resolver_imported_variable(self):
        """Test resolver if it is an imported variable
        """

        self.app.config['FLASK_LOGGING_EXTRAS']['RESOLVERS'] = {
            'extra_keyword': 'helpers.EXTRA_VAR',
        }

        with self.app.app_context():
            self.logger.info('message')

        log = self.handler.logs[0]
        self.assertIn('message extra variable', self.handler.logs)

    def test_resolver_imported_callable(self):
        """Test resolver if it is an imported callable
        """

        self.app.config['FLASK_LOGGING_EXTRAS']['RESOLVERS'] = {
            'extra_keyword': 'helpers.get_extra_keyword',
        }

        with self.app.app_context():
            self.logger.info('message')

        log = self.handler.logs[0]
        self.assertIn('message extra callable', self.handler.logs)

    def test_resolver_import_error(self):
        """Test resolver if it cannot be imported
        """

        self.app.config['FLASK_LOGGING_EXTRAS']['RESOLVERS'] = {
            'extra_keyword': 'helpers.invalid_import',
        }

        with self.app.app_context():
            self.logger.info('message')

        log = self.handler.logs[0]
        self.assertIn('message helpers.invalid_import', self.handler.logs)

    def test_resolver_none(self):
        """Test resolver if its value is ``None``
        """

        self.app.config['FLASK_LOGGING_EXTRAS']['RESOLVERS'] = {
            'extra_keyword': None,
        }

        with self.app.app_context():
            self.logger.info('message')

        log = self.handler.logs[0]
        self.assertIn('message None', self.handler.logs)


class LoggerBlueprintTestCase(TestCase):
    def setUp(self):
        # Register our logger class

        app = Flask('test_app')
        self.app = app
        app.config['FLASK_LOGGING_EXTRAS'] = {
            'BLUEPRINT': {
                'FORMAT_NAME': 'bp',
                'APP_BLUEPRINT': '<app>',
                'NO_REQUEST_BLUEPRINT': '<norequest>',
            },
        }

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
