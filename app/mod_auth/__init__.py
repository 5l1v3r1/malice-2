#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'

from flask import Blueprint

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

from . import controllers