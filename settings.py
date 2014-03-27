__author__ = 'Josh Maine'

# Define the application directory
import os
import ConfigParser

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

config = ConfigParser.ConfigParser()
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
    THREADS_PER_PAGE = 8

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data.
    CSRF_SESSION_KEY = os.urandom(24)

    ADMINS = frozenset([config.get('SITE', 'Email')])
    # Secret key for signing cookies
    SECRET_KEY = os.urandom(24)

    # Statement for enabling the development environment
    DEBUG = False
    TESTING = False

    MAIL_SERVER = config.get('Email', 'Server')
    MAIL_PORT = config.get('Email', 'Port')
    MAIL_USE_SSL = True
    MAIL_USERNAME = config.get('Email', 'Username')
    MAIL_PASSWORD = config.get('Email', 'Password')

    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = os.urandom(24)
    RECAPTCHA_PRIVATE_KEY = os.urandom(24)
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