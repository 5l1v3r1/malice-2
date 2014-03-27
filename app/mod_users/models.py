from flask.ext.login import UserMixin
from werkzeug import generate_password_hash, check_password_hash

from app import db
from app.mixins import CRUDMixin


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    # sites = db.relationship('Site', backref='site',
    #                         lazy='dynamic')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email.lower()
        self.password = self.set_password(password)

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, this_password):
        return check_password_hash(self.password, this_password)

    def __repr__(self):
        return '<User %r>' % self.name

