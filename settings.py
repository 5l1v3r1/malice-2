#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'

import os
import psutil
import ConfigParser

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'conf/config.cfg'))


class BaseConfig:
    # SERVER_NAME = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')
    DATABASE_CONNECT_OPTIONS = {}

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

    SAMPLES_PER_PAGE = 30

    # Auth Settings
    USE_LDAP = os.environ.get('USE_LDAP') or False

    # API Settings
    USE_TOKEN_AUTH = False
    USE_RATE_LIMITS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or config.get('Email', 'Server')
    MAIL_PORT = os.environ.get('MAIL_PORT') or config.get('Email', 'Port')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or config.get('Email', 'Username')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or config.get('Email', 'Password')
    DEFAULT_MAIL_SENDER = os.environ.get('MAIL_SENDER') or config.get('SITE', 'Email')
    MAIL_FLUSH_INTERVAL = 3600  # one hour
    MAIL_ERROR_RECIPIENT = os.environ.get('MAIL_ERROR_RECIPIENT') or config.get('SITE', 'ErrorEmail')

    LDAP_HOST = os.environ.get('LDAP_HOST') or config.get('LDAP', 'LDAP_HOST')
    LDAP_DOMAIN = os.environ.get('LDAP_DOMAIN') or config.get('LDAP', 'LDAP_DOMAIN')
    LDAP_AUTH_TEMPLATE = os.environ.get('LDAP_AUTH_TEMPLATE') or config.get('LDAP', 'LDAP_AUTH_TEMPLATE')
    LDAP_PROFILE_KEY = os.environ.get('LDAP_PROFILE_KEY') or config.get('LDAP', 'LDAP_PROFILE_KEY')
    LDAP_AUTH_VIEW = os.environ.get('LDAP_AUTH_VIEW') or config.get('LDAP', 'LDAP_AUTH_VIEW')

    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = os.environ.get('CAPTCHA_PUBKEY') or config.get('reCAPTCHA', 'PublicKey')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('CAPTCHA_PRIVKEY') or config.get('reCAPTCHA', 'PrivateKey')
    RECAPTCHA_OPTIONS = {'theme': 'white'}


class DevConfig(BaseConfig):
    DEBUG = True
    CSRF_ENABLED = False
    # Secret key for signing cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'users-dev.sqlite')
    MAIL_FLUSH_INTERVAL = 60  # one minute


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_ECHO = True
    CSRF_ENABLED = True
    SECRET_KEY = 'test_secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'users-test.sqlite')
    MAIL_FLUSH_INTERVAL = 60  # one minute


class ProductionConfig(BaseConfig):
    THREADS_PER_PAGE = 2 * psutil.NUM_CPUS
    USE_TOKEN_AUTH = True
    USE_RATE_LIMITS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'users.sqlite')


settings = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProductionConfig,

    'default': DevConfig
}