#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ___  ___      _ _
# |  \/  |     | (_)
# | .  . | __ _| |_  ___ ___
# | |\/| |/ _` | | |/ __/ _ \
# | |  | | (_| | | | (_|  __/
# \_|  |_/\__,_|_|_|\___\___|

__author__ = 'Josh Maine'

import logging

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.ldap import LDAP, login_required
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
# from flask.ext.pagedown import PageDown
from flask.ext.sqlalchemy import SQLAlchemy

from lib.common.logo import logo
from lib.common.exceptions import MaliceDependencyError
from lib.core.startup import (check_configs, check_version, init_logging,
                              init_modules)
from settings import settings

log = logging.getLogger()

bootstrap = Bootstrap()
# pagedown = PageDown()
mail = Mail()
db = SQLAlchemy()

ldap = LDAP()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config):
    #create_structure()

    # Define the WSGI application object
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

    # Configurations
    app.config.from_object(settings[config])
    settings[config].init_app(app)

    if not app.testing:
        logo()
        check_version()
    check_configs()
    if app.testing:
        init_logging('info')
    else:
        init_logging('debug')
    #log.setLevel(logging.DEBUG)
    init_modules()
    # Init All Flask Add-ons
    bootstrap.init_app(app)
    #pagedown.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    if app.config['USE_LDAP'] == 'yes':
        # LDAP Login
        # TODO : Test out LDAP
        app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])
        ldap.init_app(app)
    else:
        login_manager.login_view = 'auth.login'
        login_manager.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        try:
            from flask.ext.sslify import SSLify
            sslify = SSLify(app)
        except ImportError:
            from flask.ext.sslify import SSLify
            raise MaliceDependencyError("Unable to import Flask-SSLify "
                                  "(install with `pip install Flask-SSLify`)")

    # Register blueprint(s)
    from .malice import malice as malice_blueprint
    app.register_blueprint(malice_blueprint)

    from .mod_auth import mod_auth as auth_module
    app.register_blueprint(auth_module, url_prefix='/auth')

    # from app.mod_api.controller import mod_api as api_module
    # app.register_blueprint(api_module, url_prefix='/api/v1')

    return app
