import ConfigParser
import os
from flask import flash
from redis import Redis
import rethinkdb as r
from rq.decorators import job
from lib.common.utils import split_seq, list_to_string
from lib.core.database import db_insert

from app.api.virus_total_apis import PublicApi as vtPubAPI

__author__ = 'Josh Maine'

_current_dir = os.path.abspath(os.path.dirname(__file__))
BIT9_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "..", ".."))
config = ConfigParser.SafeConfigParser()
config.read(os.path.join(BIT9_ROOT, 'conf/config.cfg'))
if config.has_option('Proxie', 'HTTP') and config.has_option('Proxie', 'HTTPS'):
    vt = vtPubAPI(config.get('VirusTotal', 'PublicApiKey'),
                  dict(http=config.get('Proxie', 'HTTP'), https=config.get('Proxie', 'HTTPS')))
else:
    vt = vtPubAPI(config.get('VirusTotal', 'PublicApiKey'))


# @job('low', connection=Redis(), timeout=50)
def batch_query_virustotal(new_hash_list):
    data = {}
    #: Break list into 25 unit chuncks for VirusTotal
    vt_batch_hash_list = list(split_seq(new_hash_list, 25))
    for twentyfive_hashes in vt_batch_hash_list:
        response = vt.get_file_report(list_to_string(twentyfive_hashes))
        error = vt.handle_response_status_code(response)
        if error:
            flash(error)
        else:
            vt_results = response.json()
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
                # else:
                #     single_query_virustotal(vt_batch_hash_list[0])


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
