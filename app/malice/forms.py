#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ███╗   ███╗ █████╗ ██╗     ██╗ ██████╗███████╗
# ████╗ ████║██╔══██╗██║     ██║██╔════╝██╔════╝
# ██╔████╔██║███████║██║     ██║██║     █████╗
# ██║╚██╔╝██║██╔══██║██║     ██║██║     ██╔══╝
# ██║ ╚═╝ ██║██║  ██║███████╗██║╚██████╗███████╗
# ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝

__author__ = 'Josh Maine'

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileAllowed, FileField, FileRequired

from wtforms import BooleanField, SubmitField, TextAreaField, StringField
from wtforms.validators import Length, Required


class SearchForm(Form):
    hashes = TextAreaField('hashes')
    hash = StringField('hash')
    # submit = SubmitField("Search")
    force = BooleanField('Force', default=False)
