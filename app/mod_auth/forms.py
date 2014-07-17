#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''
__reference__ = 'https://github.com/miguelgrinberg/flasky/blob/master/app/auth/forms.py'

from flask.ext.wtf import Form, RecaptchaField

from settings import BaseConfig
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     ValidationError)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[DataRequired(),
                                             Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, '
               'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('confirm_password',
                                message='Passwords must match.')])
    confirm_password = PasswordField('Confirm password',
                                     validators=[DataRequired()])

    if BaseConfig.RECAPTCHA_ENABLE == 'yes':
        recaptcha = RecaptchaField()

    submit = SubmitField('Register')

    @staticmethod
    def validate_email(field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    @staticmethod
    def validate_username(field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('confirm_password',
                                message='Passwords must match')])
    confirm_password = PasswordField('Confirm new password',
                                     validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('confirm_password',
                                message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    @staticmethod
    def validate_email(field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    @staticmethod
    def validate_email(field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
