# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import os

_current_dir = os.path.abspath(os.path.dirname(__file__))

MALICE_ROOT = os.path.normpath(os.path.join(_current_dir, "..", ".."))
MALICE_VERSION = "v0.1-alpha"
