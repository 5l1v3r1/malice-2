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
    from shadow_server_api import ShadowServerApi
except ImportError:
    raise MaliceDependencyError("Unable to import shadow-server-api "
                                "(install with `pip install shadow-server-api`)")


class ShadowServer(Intel):
    def __init__(self):
        super(ShadowServer, self).__init__()
        self.name = "shadowserver"
        self.description = "Shadow Server - Binary Whitelist and MD5/SHA1 AV Service"
        self.categories = ["intel", "hash"]
        self.ss = ShadowServerApi()

    def batch_query(self, new_hash):
        pass

    def single_query(self, new_hash):
        data = dict(md5='md5', intel=[], av=[], file=[])
        ss_data = {}
        av_response = self.ss.get_av(new_hash)
        bin_response = self.ss.get_bintest(new_hash)

        if av_response['response_code'] == 200 and bin_response['response_code'] == 200:
            data['md5'] = new_hash.upper()
            ss_data['isfound'] = True
            ss_data['timestamp'] = datetime.datetime.utcnow()
            ss_data['module_id'] = self.name
            valid_utf8 = True
            try:
                bin_response['results']['dirname'].decode('utf-8')
            except UnicodeDecodeError:
                valid_utf8 = False
            if not valid_utf8:
                bin_response['results']['dirname'] = self.fix_unicode(bin_response['results']['dirname'])
            ss_data['av'] = av_response
            ss_data['bintest'] = bin_response
            data['intel'].append({self.name: ss_data})
        elif av_response['response_code'] == 404 and bin_response['response_code'] == 404:
            data['md5'] = new_hash.upper()
            ss_data = dict(module_id=self.name,
                             timestamp=datetime.datetime.utcnow(),
                             isfound=False,
                             requestmd5=new_hash.upper())
            data['intel'].append({self.name: ss_data})
        db_insert('files', data)
        data.clear()

    @staticmethod
    def fix_unicode(unicode_string):
        return to_unicode(unicode_string)

    def run(self, this_hash):
        self.single_query(this_hash)
