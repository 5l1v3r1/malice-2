#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import os
import ConfigParser
from api.bit9_api import Bit9Api
from lib.common.utils import split_seq
from lib.core.database import db_insert
from lib.common.exceptions import MaliceDependencyError

try:
    import rethinkdb as r
except ImportError:
    raise MaliceDependencyError("Unable to import rethinkdb "
                                "(install with `pip install rethinkdb`)")

_current_dir = os.path.abspath(os.path.dirname(__file__))
BIT9_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "..", "..", ".."))

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(BIT9_ROOT, 'conf/config.cfg'))

if config.has_section('Bit9'):
    if config.has_option('Proxie', 'HTTP') and config.has_option('Proxie', 'HTTPS'):
        bit9 = Bit9Api(config.get('Bit9', 'User'), config.get('Bit9', 'Password'),
                       dict(http=config.get('Proxie', 'HTTP'), https=config.get('Proxie', 'HTTPS')))
    else:
        bit9 = Bit9Api(config.get('Bit9', 'User'), config.get('Bit9', 'Password'))
else:
    # No config.cfg creds so try the environment or use test creds
    BIT9_USER = os.environ.get('BIT9_USER') or 'test_user'
    BIT9_PASS = os.environ.get('BIT9_PASS') or 'test_pass'
    HTTP_PROXY = os.environ.get('BIT9_USER') or False
    HTTPS_PROXY = os.environ.get('BIT9_USER') or False
    if HTTPS_PROXY:
        bit9 = Bit9Api(BIT9_USER, BIT9_PASS, dict(http=HTTP_PROXY, https=HTTPS_PROXY))
    else:
        bit9 = Bit9Api(BIT9_USER, BIT9_PASS)

# @job('low', connection=Redis(), timeout=50)
def batch_query_bit9(new_hash_list):
    data = {}
    # : Break list into 1000 unit chunks for Bit9
    bit9_batch_hash_list = list(split_seq(new_hash_list, 1000))
    for thousand_hashes in bit9_batch_hash_list:
        result = bit9.lookup_hashinfo(thousand_hashes)
        if result['response_code'] == 200 and result['results']['hashinfos']:
            for hash_info in result['results']['hashinfos']:
                if hash_info['isfound']:
                    data['md5'] = hash_info['fileinfo']['md5'].upper()
                else:
                    data['md5'] = hash_info['requestmd5'].upper()
                hash_info['timestamp'] = r.now()  # datetime.utcnow()
                data['Bit9'] = hash_info
                db_insert(data)
                data.clear()
        elif result['response_code'] == 404:
            for new_hash in new_hash_list:
                data = {'md5': new_hash.upper(),
                        'Bit9': {'timestamp': r.now(),  # datetime.utcnow(),
                                 'isfound': False,
                                 'requestmd5': new_hash.upper()}
                }
                db_insert(data)
                data.clear()
                # flash(new_hash + " - Not Found.", 'error')


# @job('low', connection=Redis(), timeout=50)
def single_query_bit9(new_hash):
    data = {}
    result = bit9.lookup_hashinfo(new_hash)
    if result['response_code'] == 200 and result['results']['hashinfo']:
        hash_info = result['results']['hashinfo']
        data['md5'] = hash_info['fileinfo']['md5'].upper()
        hash_info['isfound'] = True
        hash_info['timestamp'] = r.now()  # datetime.utcnow()
        data['Bit9'] = hash_info
    elif result['response_code'] == 404:
        data = {'md5': new_hash.upper(),
                'Bit9': {'timestamp': r.now(),  # datetime.utcnow(),
                         'isfound': False,
                         'requestmd5': new_hash.upper()}
        }
    db_insert(data)
    data.clear()