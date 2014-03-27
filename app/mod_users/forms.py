from wtforms.validators import Required, Email, EqualTo
from wtforms import TextField, PasswordField
from flask.ext.wtf import Form, validators


from app.mod_users.models import User
from app import db


def validate_login(form, field):
    user = form.get_user()

    if user is None:
        raise validators.ValidationError('Invalid user')

    if not user.check_password(form.password.data):
        raise validators.ValidationError('Invalid password')

        # if email is None:
        #     raise validators.ValidationError('Invalid email')


class LoginForm(Form):
    name = TextField(validators=[Required()])
    password = PasswordField(validators=[Required(), validate_login])

    def get_user(self):
        return db.session.query(User).filter_by(name=self.name.data).first()


class RegistrationForm(Form):
    name = TextField(validators=[Required()])
    email = TextField(validators=[Email()])
    password = PasswordField(validators=[Required(), EqualTo('confirm_password', message='Passwords did not match')])
    confirm_password = PasswordField(validators=[Required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(username=self.username.data).count() > 0:
            raise validators.ValidationError('Duplicate username')
