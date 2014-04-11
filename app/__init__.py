import os
from flask import Flask, render_template
from jinja2 import Undefined
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.datastructures import ImmutableDict
from lib.core.database import destroy_db, db_setup
from session import RethinkSessionInterface

from flask import Flask, render_template, url_for

from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

try:
    from flask.ext.ldap import LDAP
except ImportError:
    pass
try:
    from flask_mail import Mail
except ImportError:
    pass

# Define the WSGI application object
# app = Flask(__name__, instance_path='../conf')
app = Flask(__name__)

# Configurations
app.config.from_object('settings.BaseConfiguration')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
#
mail = Mail(app)
# LDAP Login
# ldap = LDAP(app)
# # TODO - Test out LDAP
# app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])
# Regular Login
login_manager = LoginManager(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_users.views import mod_user as user_module
from app.mod_api.controller import mod_api as api_module

# Register blueprint(s)
app.register_blueprint(user_module)
app.register_blueprint(api_module)

#add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "users.login_view"

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()

# app.session_interface = RethinkSessionInterface(db='session')

app.wsgi_app = ProxyFix(app.wsgi_app)

from app import views
# from app.mod_api import routes
