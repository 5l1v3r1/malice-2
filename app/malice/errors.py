#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ███╗   ███╗ █████╗ ██╗     ██╗ ██████╗███████╗
# ████╗ ████║██╔══██╗██║     ██║██╔════╝██╔════╝
# ██╔████╔██║███████║██║     ██║██║     █████╗
# ██║╚██╔╝██║██╔══██║██║     ██║██║     ██╔══╝
# ██║ ╚═╝ ██║██║  ██║███████╗██║╚██████╗███████╗
# ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from flask import jsonify, render_template, request

from . import malice

# TODO: Fix this
github = "https://github.com/blacktop/malice"


@malice.app_errorhandler(400)
def bad_request(reason):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'bad request'})
        response.status_code = 400
        return response
    return render_template('error/400.html',
                           reason=reason,
                           my_github=github), 400


@malice.app_errorhandler(401)
def unauthorized(reason):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'unauthorized'})
        response.status_code = 401
        return response
    return render_template('error/401.html',
                           reason=reason,
                           my_github=github), 401


@malice.app_errorhandler(403)
def forbidden(reason):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'unauthorized'})
        response.status_code = 403
        return response
    return render_template('error/404.html',
                           reason=reason,
                           my_github=github), 403


@malice.app_errorhandler(404)
def page_not_found(reason):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'unauthorized'})
        response.status_code = 404
        return response
    return render_template('error/404.html',
                           reason=reason,
                           my_github=github), 404


@malice.app_errorhandler(413)
def request_entity_too_large(reason):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'request entity too large'})
        response.status_code = 413
        return response
    return render_template('error/413.html',
                           reason=reason,
                           my_github=github), 413


@malice.app_errorhandler(500)
def internal_server_error(reason):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('error/500.html',
                           reason=reason,
                           my_github=github), 500
