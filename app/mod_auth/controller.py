#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

__reference__ = 'https://github.com/miguelgrinberg/flasky/blob/master/app/auth/views.py'

from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import (current_user, login_required, login_user, logout_user)

from . import mod_auth as auth
from .. import db
from ..email import send_email
from ..models import User
from .forms import (ChangeEmailForm, ChangePasswordForm, LoginForm, PasswordResetForm, PasswordResetRequestForm,
                    RegistrationForm)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        print request.endpoint
        if not current_user.confirmed:
            if request.endpoint == None or request.endpoint[:5] != 'auth.':
                resend_confirmation()
                return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('malice.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('malice.index'))
        flash('Invalid username or password.', 'warning')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')


# @login_required TODO: Uncomment this!!
def logout():
    try:
        logout_user()
    except Exception as e:
        print e
        pass
    flash('You have been logged out.', 'warning')
    return redirect(url_for('malice.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('malice.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!', 'warning')
    else:
        flash('The confirmation link is invalid or has expired.', 'warning')
    return redirect(url_for('malice.index'), code=307)


@auth.route('/confirm', methods=['POST'])
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.', 'warning')
    return redirect(url_for('malice.index'), code=307)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.', 'warning')
            return redirect(url_for('malice.index'))
        else:
            flash('Invalid password.', 'warning')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('malice.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email,
                       'Reset Your Password',
                       'auth/email/reset_password',
                       user=user,
                       token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been ' 'sent to you.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/password_reset_request.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('malice.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('malice.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.', 'warning')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('malice.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email,
                       'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user,
                       token=token)
            flash('An email with instructions to confirm your new email ' 'address has been sent to you.', 'warning')
            return redirect(url_for('malice.index'))
        else:
            flash('Invalid email or password.', 'warning')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'warning')
    else:
        flash('Invalid request.', 'warning')
    return redirect(url_for('malice.index'))
