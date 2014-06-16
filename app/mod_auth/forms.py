__author__ = 'Josh Maine'

# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form  # , RecaptchaField

from wtforms import PasswordField, TextField  # BooleanField
from wtforms.validators import Email, Required


# Define the login form (WTForms)
class LoginForm(Form):
    email = TextField('Email Address', [Email(),
                      Required(message='Forgot your email address?')])
    password = PasswordField('Password',
                      [Required(message='Must provide a password.')])
