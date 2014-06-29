#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import unittest

from flask import url_for

from app import create_app, db
from app.models import Role  # User


class MaliceURLsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home(self):
        response = self.client.get(url_for('malice.index'))
        self.assertTrue(response.status_code == 200)

    def test_samples(self):
        response = self.client.get(url_for('malice.samples'))
        self.assertTrue(response.status_code == 200)

    def test_intel(self):
        response = self.client.get(url_for('malice.intel'))
        self.assertTrue(response.status_code == 200)

    def test_upload(self):
        response = self.client.get(url_for('malice.upload'))
        self.assertTrue(response.status_code == 405)

    def test_system(self):
        response = self.client.get(url_for('malice.system'))
        self.assertTrue(response.status_code == 200)

    def test_help(self):
        response = self.client.get(url_for('malice.help'))
        self.assertTrue(response.status_code == 200)

    def test_login(self):
        response = self.client.get(url_for('auth.login'))
        self.assertTrue(response.status_code == 200)

    def test_register(self):
        response = self.client.get(url_for('auth.register'))
        self.assertTrue(response.status_code == 200)

    def test_reset(self):
        response = self.client.get(url_for('auth.password_reset_request'))
        self.assertTrue(response.status_code == 200)

    def test_unconfirmed(self):
        response = self.client.get(url_for('auth.unconfirmed'))
        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.location == 'http://127.0.0.1/')

    def test_logout(self):
        response = self.client.get(url_for('auth.logout'))
        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.location == 'http://127.0.0.1/')

    def test_confirm(self):
        response = self.client.get(url_for('auth.resend_confirmation'))
        self.assertTrue(response.status_code == 405)

    def test_change_password(self):
        response = self.client.get(url_for('auth.change_password'))
        self.assertTrue(response.status_code == 200)

    def test_change_email(self):
        response = self.client.get(url_for('auth.change_email_request'))
        self.assertTrue(response.status_code == 200)
