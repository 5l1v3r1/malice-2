__author__ = 'Josh Maine'

# Import flask dependencies
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug import check_password_hash, generate_password_hash

from app import db
from app.mod_auth.forms import LoginForm
from app.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@mod_auth.route('/signin/', methods=['GET', 'POST'])
def signin():
    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():
        me = User(name='Test', email='test@email.com', password='password')
        db.session.add(me)
        db.session.commit()
        all_users = User.query.all()
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id

            flash('Welcome %s' % user.name)

            return redirect(url_for('auth.home'))

        flash('Wrong email or password', 'error')

    return render_template("auth/signin.html", form=form)
