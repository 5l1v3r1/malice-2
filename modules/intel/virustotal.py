# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import os
import ConfigParser
from flask import flash
from lib.core.database import db_insert
from lib.common.utils import split_seq, list_to_string
from lib.common.exceptions import MaliceDependencyError
from lib.common.constants import MALICE_ROOT

try:
    from virus_total_apis import PublicApi as vtPubAPI
except ImportError:
    raise MaliceDependencyError("Unable to import virustotal-api "
                                "(install with `pip install virustotal-api`)")
try:
    import rethinkdb as r
except ImportError:
    raise MaliceDependencyError("Unable to import rethinkdb "
                                "(install with `pip install rethinkdb`)")


def get_config():
    VT_API, HTTP_PROXY, HTTPS_PROXY = None, None, None
    # Read config files
    intel_config = ConfigParser.SafeConfigParser()
    malice_config = ConfigParser.SafeConfigParser()
    intel_config.read(os.path.join(MALICE_ROOT, 'conf/intel.conf'))
    malice_config.read(os.path.join(MALICE_ROOT, 'conf/malice.conf'))
    # Parse config.cfg file
    if intel_config.has_section('virustotal') and intel_config.get('virustotal', 'enabled') == "yes":
        VT_API = intel_config.get('virustotal', 'pubapikey')
        if malice_config.has_section('proxie') and malice_config.get('proxie', 'enabled') == "yes":
            if malice_config.has_option('proxie', 'http'):
                HTTP_PROXY = malice_config.get('proxie', 'http')
            if malice_config.has_option('proxie', 'https'):
                HTTPS_PROXY = malice_config.get('proxie', 'https')
    else:
        # No config.cfg creds so try the environment or use test creds
        VT_API = os.environ.get('VT_API') or 'test_api'
        HTTP_PROXY = os.environ.get('HTTP_PROXY') or False
        HTTPS_PROXY = os.environ.get('HTTPS_PROXY') or False

    return VT_API, HTTP_PROXY, HTTPS_PROXY


VT_API, HTTP_PROXY, HTTPS_PROXY = get_config()

if HTTPS_PROXY:
    vt = vtPubAPI(VT_API, dict(http=HTTP_PROXY, https=HTTPS_PROXY))
else:
    vt = vtPubAPI(VT_API)

# @job('low', connection=Redis(), timeout=50)
def batch_query_virustotal(new_hash_list):
    data = {}
    #: Break list into 25 unit chuncks for VirusTotal
    vt_batch_hash_list = list(split_seq(new_hash_list, 25))
    for twentyfive_hashes in vt_batch_hash_list:
        response = vt.get_file_report(list_to_string(twentyfive_hashes))
        if hasattr(response, 'error'):
            flash(response['error'])
        else:
            vt_results = response['results']
            for result in vt_results:
                if result['response_code']:
                    # print "Evilness: %d" % result['positives']
                    data['md5'] = result['md5'].upper()
                else:
                    data['md5'] = result['resource'].upper()
                result['timestamp'] = r.now()  # datetime.utcnow()
                data['VirusTotal'] = result
                db_insert(data)
                data.clear()


# @job('low', connection=Redis(), timeout=50)
def single_query_virustotal(new_hash):
    data = {}
    response = vt.get_file_report(new_hash)
    # error = vt.handle_response_status_code(response)
    if response['response_code'] == 200:
        vt_result = response['results']
        if vt_result['response_code']:
            # print "Evilness: %d" % vt_result['positives']
            data['md5'] = vt_result['md5'].upper()
        else:
            data['md5'] = vt_result['resource'].upper()
        vt_result['timestamp'] = r.now()  # datetime.utcnow()
        data['VirusTotal'] = vt_result
        db_insert(data)
        data.clear()
    else:
        flash(response['error'])
