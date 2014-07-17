#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from flask.ext.wtf import Form, RecaptchaField, validators

from app import db
from app.mod_users.models import User
from wtforms import PasswordField, TextField
from wtforms.validators import Email, EqualTo, Required


def validate_login(form, field):
    user = form.get_user()

    if user is None:
        raise validators.ValidationError('Invalid user')

    if not user.verify_password(form.password.data):
        raise validators.ValidationError('Invalid password')

        # if email is None:
        #     raise validators.ValidationError('Invalid email')


class LoginForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required(), validate_login])

    def get_user(self):
        return db.session.query(User).filter_by(name=self.name.data).first()


class RegistrationForm(Form):
    username = TextField(validators=[Required()])
    email = TextField(validators=[Email()])
    password = PasswordField(validators=[Required(), EqualTo('confirm_password', message='Passwords did not match')])
    confirm_password = PasswordField(validators=[Required()])
    recaptcha = RecaptchaField()

    def validate_login(self, field):
        if db.session.query(User).filter_by(username=self.username.data).count() > 0:
            raise validators.ValidationError('Duplicate username')
