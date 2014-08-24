#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''
__reference__ = 'https://github.com/miguelgrinberg/flasky/blob/master/config.py'

import ConfigParser
import os

import psutil
from lib.common.constants import MALICE_ROOT

UPLOAD_FOLDER = os.path.join(MALICE_ROOT, 'static/uploads')

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(MALICE_ROOT, 'conf/malice.conf'))


class BaseConfig:
    # SERVER_NAME = ''
    DATABASE_CONNECT_OPTIONS = {}
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_RECORD_QUERIES = True
    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 1

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for signing the data.
    CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY')

    # Secret key for signing cookies
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SSL_DISABLE = True

    SAMPLES_PER_PAGE = 30

    MAX_CONTENT_LENGTH = os.environ.get('MAX_CONTENT_LENGTH') or \
        config.get('malice', 'upload_max_size') or \
        50 * 1024 * 1024  # 50MB

    # API Settings
    USE_TOKEN_AUTH = False
    USE_RATE_LIMITS = False

    URL = os.environ.get('URL') or config.get('malice', 'url')
    EMAIL = os.environ.get('EMAIL') or config.get('malice', 'email')
    GITHUB = os.environ.get('GITHUB') or config.get('malice', 'github')

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or config.get('email', 'server')
    MAIL_PORT = os.environ.get('MAIL_PORT') or config.get('email', 'port')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or \
        config.get('email', 'username')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or \
        config.get('email', 'password')
    MALICE_MAIL_SUBJECT_PREFIX = '[Malice]'
    DEFAULT_MAIL_SENDER = os.environ.get('MAIL_SENDER') or \
        config.get('malice', 'email')
    MALICE_ADMIN = os.environ.get('MALICE_ADMIN') or \
        config.get('malice', 'admin')
    MAIL_FLUSH_INTERVAL = 3600  # one hour
    MAIL_ERROR_RECIPIENT = os.environ.get('MAIL_ERROR_RECIPIENT') or \
        config.get('malice', 'erroremail')

    # Auth Settings
    USE_LDAP = os.environ.get('USE_LDAP') or config.get('ldap', 'enabled') or False
    LDAP_HOST = os.environ.get('LDAP_HOST') or config.get('ldap', 'host')
    LDAP_DOMAIN = os.environ.get('LDAP_DOMAIN') or config.get('ldap', 'domain')
    LDAP_SEARCH_BASE = os.environ.get('LDAP_SEARCH_BASE') or config.get('ldap', 'searchbase')
    LDAP_AUTH_TEMPLATE = os.environ.get('LDAP_AUTH_TEMPLATE') or config.get('ldap', 'auth_temp')
    # LDAP_PROFILE_KEY = os.environ.get('LDAP_PROFILE_KEY') or config.get('ldap', 'profile_key')
    LDAP_AUTH_VIEW = os.environ.get('LDAP_AUTH_VIEW') or config.get('ldap', 'auth_view')

    RECAPTCHA_ENABLE = os.environ.get('RECAPTCHA_ENABLE') or config.get('reCAPTCHA', 'enabled') or 'no'
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = os.environ.get('CAPTCHA_PUBKEY') or config.get('reCAPTCHA', 'pubkey')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('CAPTCHA_PRIVKEY') or config.get('reCAPTCHA', 'privkey')
    RECAPTCHA_OPTIONS = {'theme': 'white'}

    @staticmethod
    def init_app(app):
        pass

class DevConfig(BaseConfig):
    DEBUG = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    # Secret key for signing cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(MALICE_ROOT, 'users-dev.sqlite')
    MAIL_FLUSH_INTERVAL = 60  # one minute


class TestConfig(BaseConfig):
    TESTING = True
    # SQLALCHEMY_ECHO = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test_secret'
    SERVER_NAME = '127.0.0.1'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(MALICE_ROOT, 'users-test.sqlite')
    MAIL_FLUSH_INTERVAL = 60  # one minute


class ProductionConfig(BaseConfig):
    THREADS_PER_PAGE = 2 * psutil.NUM_CPUS
    USE_TOKEN_AUTH = True
    USE_RATE_LIMITS = True
    SSL_DISABLE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(MALICE_ROOT, 'users.sqlite')

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.DEFAULT_MAIL_SENDER,
            toaddrs=[cls.MALICE_ADMIN],
            subject=cls.MALICE_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


settings = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,

    'default': DevConfig
}
