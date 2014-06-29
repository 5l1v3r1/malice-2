#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from flask import flash, g, redirect, render_template, request, session, url_for
from flask.ext.login import (current_user, login_required, login_user,
                             logout_user)

from app import db, login_manager
from app.mod_users.models import User
from forms import LoginForm, RegistrationForm

from . import mod_user


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
        return redirect(request.args.get("next") or url_for("malice.index"))
    return render_template('users/../templates/auth/login.html', form=form)


@mod_user.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(username=form.name.data,
                    email=form.email.data,
                    password=form.password.data)
        # form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('malice.index'))
    return render_template('users/../templates/auth/register.html', form=form)


@login_required
@mod_user.route('/logout/')
def logout_view():
    logout_user()
    return redirect(url_for('malice.index'))
