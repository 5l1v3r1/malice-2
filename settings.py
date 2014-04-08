__author__ = 'Josh Maine'

# Define the application directory
import os
import psutil
import ConfigParser

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# TODO - Store copies of uploaded binaries in S3 for a month (or permanently) so that Malice can auto rescan
# UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(BASE_DIR, 'conf/config.cfg'))

class BaseConfiguration(object):
    # SERVER_NAME = ''

    # Define the database - we are working with
    # SQLite for this example
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')
    DATABASE_CONNECT_OPTIONS = {}

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2 #* psutil.NUM_CPUS

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data.
    CSRF_SESSION_KEY = os.urandom(24)
    if config.has_section('SITE'):
        ADMINS = frozenset([config.get('SITE', 'Email')])
    else:
        ADMINS = frozenset(['example@test.com'])
    # Secret key for signing cookies
    SECRET_KEY = os.urandom(24)

    # Statement for enabling the development environment
    DEBUG = False
    TESTING = False

    if config.has_section('Email'):
        MAIL_SERVER = config.get('Email', 'Server')
        MAIL_PORT = config.get('Email', 'Port')
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_DEBUG = DEBUG
        MAIL_USERNAME = config.get('Email', 'Username')
        MAIL_PASSWORD = config.get('Email', 'Password')
        DEFAULT_MAIL_SENDER = ADMINS

    if config.has_section('LDAP'):
        LDAP_HOST = config.get('LDAP', 'LDAP_HOST')
        LDAP_DOMAIN = config.get('LDAP', 'LDAP_DOMAIN')
        LDAP_AUTH_TEMPLATE = config.get('LDAP', 'LDAP_AUTH_TEMPLATE')
        LDAP_PROFILE_KEY = config.get('LDAP', 'LDAP_PROFILE_KEY')
        LDAP_AUTH_VIEW = config.get('LDAP', 'LDAP_AUTH_VIEW')

    if config.has_section('reCAPTCHA'):
        RECAPTCHA_USE_SSL = False
        RECAPTCHA_PUBLIC_KEY = config.get('reCAPTCHA', 'PublicKey')
        RECAPTCHA_PRIVATE_KEY = config.get('reCAPTCHA', 'PrivateKey')
        RECAPTCHA_OPTIONS = {'theme': 'white'}


class TestConfiguration(BaseConfiguration):
    TESTING = True
    CSRF_ENABLED = False
    DATABASE = 'tests.db'
    DATABASE_PATH = os.path.join(BASE_DIR, DATABASE)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # + DATABASE_PATH


class DebugConfiguration(BaseConfiguration):
    DEBUG = True
    # SQLALCHEMY_ECHO = True