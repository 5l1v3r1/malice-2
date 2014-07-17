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

from wtforms import BooleanField, SubmitField, TextAreaField, TextField
from wtforms.validators import Length, Required


class SearchForm(Form):
    hashes = TextAreaField('hashes')
    label = TextField('label')
    submit = SubmitField("Search")
    force = BooleanField('Force', default=False)
