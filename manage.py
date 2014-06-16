#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# `7MMM.     ,MMF'      db      `7MMF'      `7MMF' .g8"""bgd `7MM"""YMM
#   MMMb    dPMM       ;MM:       MM          MM .dP'     `M   MM    `7
#   M YM   ,M MM      ,V^MM.      MM          MM dM'       `   MM   d
#   M  Mb  M' MM     ,M  `MM      MM          MM MM            MMmmMM
#   M  YM.P'  MM     AbmmmqMA     MM      ,   MM MM.           MM   Y  ,
#   M  `YM'   MM    A'     VML    MM     ,M   MM `Mb.     ,'   MM     ,M
# .JML. `'  .JMML..AMA.   .AMMA..JMMmmmmMMM .JMML. `"bmmmd'  .JMMmmmmMMM

__author__ = 'Josh Maine'

import os

from flask.ext.script import Manager, prompt_bool, Server

from app import create_app, db
from app.mod_users.models import User
from lib.core.database import db_setup, destroy_db

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2 and '#' not in var[0]:
            os.environ[var[0]] = var[1]


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


@manager.command
def test():
    """Run test suite"""
    from subprocess import call

    call(['nosetests', '-v',
          '--with-coverage', '--cover-package=app', '--cover-branches',
          '--cover-erase', '--cover-html', '--cover-html-dir=cover'])


@manager.command
def adduser(email, username, admin=False):
    """Register a new user."""
    from getpass import getpass

    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys

        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(email=email, username=username, password=password,
                is_admin=admin)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))


@manager.command
def dropdb():
    """Drops database tables"""
    if prompt_bool("Are you sure you want to lose all your data"):
        destroy_db()
        db.drop_all()
        db_setup()
        db.create_all()


@manager.command
def createdb():
    """Create database tables"""
    db_setup()
    db.create_all()


@manager.command
def runserver():
    """Start the server"""
    # TODO : Remove use_reloader when Flask 1.0 comes out
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)


if __name__ == '__main__':
    manager.run()
