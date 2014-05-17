#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ███╗   ███╗ █████╗ ██╗     ██╗ ██████╗███████╗
# ████╗ ████║██╔══██╗██║     ██║██╔════╝██╔════╝
# ██╔████╔██║███████║██║     ██║██║     █████╗
# ██║╚██╔╝██║██╔══██║██║     ██║██║     ██╔══╝
# ██║ ╚═╝ ██║██║  ██║███████╗██║╚██████╗███████╗
# ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝

__author__ = 'Josh Maine'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.ldap import LDAP
# from flask.ext.pagedown import PageDown
from flask.ext.mail import Mail
from settings import config

db = SQLAlchemy()
# pagedown = PageDown()
mail = Mail()
ldap = LDAP()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    # Define the WSGI application object
    app = Flask(__name__)
    # Configurations
    app.config.from_object(config[config_name])

    if True:
    # if not app.config['DEBUG'] and not app.config['TESTING']:
        # configure logging for production

        # email errors to the administrators
        if app.config.get('MAIL_ERROR_RECIPIENT') is not None:
            import logging
            from logging.handlers import SMTPHandler

            credentials = None
            secure = None
            if app.config.get('MAIL_USERNAME') is not None:
                credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                if app.config['MAIL_USE_TLS'] is not None:
                    secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['DEFAULT_MAIL_SENDER'],
                toaddrs=[app.config['MAIL_ERROR_RECIPIENT']],
                subject='[Malice] Application Error',
                credentials=credentials,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # send standard logs to syslog
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

    db.init_app(app)
    # pagedown.init_app(app)
    mail.init_app(app)
    if app.config['USE_LDAP']:
        # LDAP Login
        ldap.init_app(app)
        # TODO : Test out LDAP
        app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])
    else:
        login_manager.init_app(app)

    # Register blueprint(s)
    from .malice import malice as malice_blueprint
    app.register_blueprint(malice_blueprint)

    from app.mod_users.routes import mod_user as user_module
    app.register_blueprint(user_module, url_prefix='/auth')

    # from app.mod_api.controller import mod_api as api_module
    # app.register_blueprint(api_module, url_prefix='/api/v1')

    from app.emails import start_email_thread
    @app.before_first_request
    def before_first_request():
        start_email_thread()

    # from werkzeug.contrib.fixers import ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    # from app import views
    return app