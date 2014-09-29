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
from lib.common.utils import split_seq
from lib.core.database import db_insert

# try:
#     import rethinkdb as r
# except ImportError:
#     raise MaliceDependencyError("Unable to import rethinkdb "
#                                 "(install with `pip install rethinkdb`)")
try:
    from bit9_api import Bit9Api
except ImportError:
    raise MaliceDependencyError("Unable to import bit9-api "
                                "(install with `pip install bit9-api`)")


class Bit9(Intel):
    def __init__(self):
        super(Bit9, self).__init__()
        self.name = "bit9"
        self.description = "Bit9 API for their Cyber Forensics Service"
        self.site_url = "https://github.com/blacktop/bit9-api"
        self.categories = ["intel", "hash"]
        # self.ss = ShadowServerApi()
        BIT9_USER, BIT9_PASS, HTTP_PROXY, HTTPS_PROXY = self.get_config()
        if HTTPS_PROXY:
            self.bit9 = Bit9Api(BIT9_USER, BIT9_PASS, dict(http=HTTP_PROXY, https=HTTPS_PROXY))
        else:
            self.bit9 = Bit9Api(BIT9_USER, BIT9_PASS)

    @staticmethod
    def get_config():
        BIT9_USER, BIT9_PASS, HTTP_PROXY, HTTPS_PROXY = None, None, False, False
        # Read config.cfg file
        intel_config = ConfigParser.SafeConfigParser()
        malice_config = ConfigParser.SafeConfigParser()
        intel_config.read(os.path.join(MALICE_ROOT, 'conf/intel.conf'))
        malice_config.read(os.path.join(MALICE_ROOT, 'conf/malice.conf'))
        # Parse config.cfg file
        if intel_config.has_section('bit9') and intel_config.get('bit9', 'enabled') == "yes":
            BIT9_USER = os.environ.get('BIT9_USER') or \
                intel_config.get('bit9', 'user') or 'test_user'
            BIT9_PASS = os.environ.get('BIT9_PASS') or \
                intel_config.get('bit9', 'password') or 'test_pass'
            if malice_config.has_option('proxie', 'http') or \
                    malice_config.has_option('proxie', 'https'):
                HTTP_PROXY = os.environ.get('HTTP_PROXY') or \
                    malice_config.get('proxie', 'http') or False
                HTTPS_PROXY = os.environ.get('HTTPS_PROXY') or \
                    malice_config.get('proxie', 'https') or False
        return BIT9_USER, BIT9_PASS, HTTP_PROXY, HTTPS_PROXY

    # @job('low', connection=Redis(), timeout=50)
    def batch_query_bit9(self, new_hash_list):
        data = {}
        # : Break list into 1000 unit chunks for Bit9
        bit9_batch_hash_list = list(split_seq(new_hash_list, 1000))
        for thousand_hashes in bit9_batch_hash_list:
            result = self.bit9.lookup_hashinfo(thousand_hashes)
            if result['response_code'] == 200 and result['results']['hashinfos']:
                for hash_info in result['results']['hashinfos']:
                    if hash_info['isfound']:
                        data['md5'] = hash_info['fileinfo']['md5'].upper()
                    else:
                        data['md5'] = hash_info['requestmd5'].upper()
                    # hash_info['timestamp'] = r.now()  # datetime.utcnow()
                    hash_info['timestamp'] = datetime.datetime.utcnow(),
                    data['bit9'] = hash_info
                    db_insert('files', data)
                    return data
                    # data.clear()
            elif result['response_code'] == 404:
                for new_hash in new_hash_list:
                    data = {'md5': new_hash.upper(),
                            # 'Bit9': {'timestamp': r.now(),  # datetime.utcnow(),
                            'bit9': {'timestamp': datetime.datetime.utcnow(),
                                     'isfound': False,
                                     'requestmd5': new_hash.upper()}
                            }
                    db_insert('files', data)
                    # data.clear()
                    return data

    # @job('low', connection=Redis(), timeout=50)
    def single_query_bit9(self, new_hash):
        data = dict(md5='md5', intel=[], av=[], file=[])
        result = self.bit9.lookup_hashinfo(new_hash)
        if result['response_code'] == 200 and result['results']['hashinfo']:
            hash_info = result['results']['hashinfo']
            # data['_id'] = hash_info['fileinfo']['md5'].upper()
            data['md5'] = hash_info['fileinfo']['md5'].upper()
            hash_info['isfound'] = True
            # hash_info['timestamp'] = r.now()  # datetime.utcnow()
            hash_info['timestamp'] = datetime.datetime.utcnow()
            hash_info['module_id'] = 'bit9'
            # data['intel'].append(hash_info)
            data['intel'].append(dict(bit9=hash_info))
        # elif result['response_code'] == 404:
        else:
            data['md5'] = new_hash.upper()
            bit9_data = dict(module_id='bit9',
                             timestamp=datetime.datetime.utcnow(),
                             isfound=False,
                             error=result.error,
                             requestmd5=new_hash.upper())
            data['intel'].append(dict(bit9=bit9_data))
        db_insert('files', data)
        # data.clear()
        return data

    def run(self, query_data):
        """

        :param query_data:
        """
        if query_data:
            if isinstance(query_data, basestring):
                return self.single_query_bit9(query_data)
            else:
                return self.batch_query_bit9(query_data)
