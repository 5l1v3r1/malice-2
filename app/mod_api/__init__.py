#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'

from flask import Blueprint, request, g

api = Blueprint('api', __name__)

from app.mod_users.models import User
from . import errors


@api.before_request
def before_api_request():
    if request.json is None:
        return errors.bad_request('Invalid JSON in body.')
    token = request.json.get('token')
    if not token:
        return errors.unauthorized('Authentication token not provided.')
    user = User.validate_api_token(token)
    if not user:
        return errors.unauthorized('Invalid authentication token.')
    g.current_user = user
