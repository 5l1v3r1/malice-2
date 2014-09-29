#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import ConfigParser
import datetime
import os

from lib.common.abstracts import Intel
from lib.common.constants import MALICE_ROOT
from lib.common.exceptions import MaliceDependencyError
from lib.common.utils import split_seq, to_unicode
from lib.core.database import db_insert

try:
    from team_cymru_api import TeamCymruApi
except ImportError:
    raise MaliceDependencyError("Unable to import team-cymru-api "
                                "(install with `pip install team-cymru-api`)")


class TeamCymru(Intel):
    def __init__(self):
        super(TeamCymru, self).__init__()
        self.name = "teamcymru"
        self.description = "Team Cymru - Malware Hash Registry API"
        self.site_url = "https://github.com/blacktop/team-cymru-api"
        self.categories = ["intel", "hash"]
        self.tc = TeamCymruApi()

    def batch_query(self, hash_list):
        pass

    def single_query(self, new_hash):
        data = dict(md5='md5', intel=[], av=[], file=[])
        tc_data = {}
        tc_response = self.tc.get_cymru(new_hash)

        if tc_response['response_code'] == 200:
            data['md5'] = new_hash.upper()
            tc_data['isfound'] = True
            tc_data['timestamp'] = datetime.datetime.utcnow()
            tc_data['module_id'] = self.name
            tc_response = self.fix_unicode(tc_response)
            tc_data['response'] = tc_response
            data['intel'].append({self.name: tc_data})
        elif tc_response['response_code'] == 404:
            data['md5'] = new_hash.upper()
            tc_data = dict(module_id=self.name,
                           timestamp=datetime.datetime.utcnow(),
                           isfound=False,
                           requestmd5=new_hash.upper())
            data['intel'].append({self.name: tc_data})
        db_insert('files', data)
        return data
        # data.clear()

    def fix_unicode(self, data):
        for key, value in data.iteritems():
            valid_utf8 = True
            try:
                if isinstance(value, dict):
                    data[key] = self.fix_unicode(value)
                if isinstance(value, basestring):
                    value.decode('utf-8')
            except UnicodeDecodeError:
                valid_utf8 = False
            if not valid_utf8:
                data[key] = to_unicode(value)
        return data

    def run(self, this_hash):
        return self.single_query(this_hash)
