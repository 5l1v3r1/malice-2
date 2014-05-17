# !/usr/bin/env python
# -*- coding: utf-8 -*-

# ███╗   ███╗ █████╗ ██╗     ██╗ ██████╗███████╗
# ████╗ ████║██╔══██╗██║     ██║██╔════╝██╔════╝
# ██╔████╔██║███████║██║     ██║██║     █████╗
# ██║╚██╔╝██║██╔══██║██║     ██║██║     ██╔══╝
# ██║ ╚═╝ ██║██║  ██║███████╗██║╚██████╗███████╗
# ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝

__author__ = 'Josh Maine'

from . import malice
from flask import render_template

# TODO: Fix this
github = "https://github.com/blacktop/malice"

@malice.errorhandler(400)
def page_not_found(reason):
    return render_template('error/400.html', reason=reason, my_github=github), 400


@malice.errorhandler(404)
def page_not_found(reason):
    return render_template('error/404.html', reason=reason, my_github=github), 404


@malice.errorhandler(413)
def page_not_found(reason):
    return render_template('error/413.html', reason=reason, my_github=github), 413


@malice.errorhandler(500)
def page_not_found(reason):
    return render_template('error/500.html', reason=reason, my_github=github), 500
