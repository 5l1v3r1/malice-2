from flask import render_template, flash, redirect, session, url_for, request, g
from . import mod_user
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import db, login_manager
from forms import LoginForm, RegistrationForm
from app.mod_users.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@mod_user.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = form.get_user()
        login_user(user)
        # g.user = user.name
        flash("Logged in successfully.", 'error')
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('users/login.html', form=form)

@mod_user.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(username=form.name.data, email=form.email.data, password=form.password.data)
        # form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('users/register.html', form=form)

@login_required
@mod_user.route('/logout/')
def logout_view():
    logout_user()
    return redirect(url_for('index'))