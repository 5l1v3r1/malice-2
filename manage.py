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
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''
__reference__ = 'https://github.com/miguelgrinberg/flasky/blob/master/manage.py'

import os

COV = None
if os.environ.get('MALICE_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2 and '#' not in var[0]:
            os.environ[var[0]] = var[1]

from flask.ext.script import Manager, prompt_bool

from app import create_app, db
from app.models import User, Role, Permission
from lib.core.database import db_setup, destroy_db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


@manager.command
def test(with_coverage=False):
    """Run the unit tests."""
    if with_coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def adduser(email, username):
    """Register a new user."""
    from getpass import getpass

    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys

        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(email=email, username=username, password=password)
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

    # create user roles
    Role.insert_roles()

    # create self-follows for all users
    User.add_self_follows()


@manager.command
def runserver():
    """Start the server"""
    # TODO : Remove use_reloader when Flask 1.0 comes out
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)


if __name__ == '__main__':
    manager.run()
