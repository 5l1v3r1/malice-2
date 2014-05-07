#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'

from flask import Blueprint
mod_user = Blueprint('users', __name__)
from . import routes