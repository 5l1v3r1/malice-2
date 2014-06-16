#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import ConfigParser
import os

from lib.common.abstracts import Intel
from lib.common.constants import MALICE_ROOT
from lib.common.exceptions import MaliceDependencyError
from lib.common.utils import split_seq
from lib.core.database import db_insert

try:
    from team_cymru_api import TeamCymruApi
except ImportError:
    raise MaliceDependencyError("Unable to import team-cymru-api "
                                "(install with `pip install team-cymru-api`)")


class TeamCymru(Intel):
    pass