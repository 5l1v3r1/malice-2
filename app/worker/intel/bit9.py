import ConfigParser
import os
from redis import Redis
import rethinkdb as r
from rq.decorators import job
from lib.common.utils import split_seq
from app.api.bit9_api import Bit9Api
from lib.core.database import db_insert

__author__ = 'Josh Maine'

_current_dir = os.path.abspath(os.path.dirname(__file__))
BIT9_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "..", ".."))
config = ConfigParser.SafeConfigParser()
config.read(os.path.join(BIT9_ROOT, 'conf/config.cfg'))
if config.has_option('Proxie', 'HTTP') and config.has_option('Proxie', 'HTTPS'):
    bit9 = Bit9Api(config.get('Bit9', 'User'), config.get('Bit9', 'Password'),
                   dict(http=config.get('Proxie', 'HTTP'), https=config.get('Proxie', 'HTTPS')))
else:
    bit9 = Bit9Api(config.get('Bit9', 'User'), config.get('Bit9', 'Password'))

# @job('low', connection=Redis(), timeout=50)
def batch_query_bit9(new_hash_list):
    data = {}
    #: Break list into 1000 unit chunks for Bit9
    bit9_batch_hash_list = list(split_seq(new_hash_list, 1000))
    for thousand_hashes in bit9_batch_hash_list:
        result = bit9.lookup_batch_md5(thousand_hashes)
        if result.status_code == 200 and result.json()['hashinfos']:
            for hash_info in result.json()['hashinfos']:
                if hash_info['isfound']:
                    data['md5'] = hash_info['fileinfo']['md5'].upper()
                else:
                    data['md5'] = hash_info['requestmd5'].upper()
                hash_info['timestamp'] = r.now()  # datetime.utcnow()
                data['Bit9'] = hash_info
                db_insert(data)
                data.clear()
        elif result.status_code == 404:
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
    result = bit9.lookup_md5(new_hash)
    if result.status_code == 200 and result.json()['hashinfo']:
        hash_info = result.json()['hashinfo']
        data['md5'] = hash_info['fileinfo']['md5'].upper()
        hash_info['isfound'] = True
        hash_info['timestamp'] = r.now()  # datetime.utcnow()
        data['Bit9'] = hash_info
    elif result.status_code == 404:
        data = {'md5': new_hash.upper(),
                'Bit9': {'timestamp': r.now(),  # datetime.utcnow(),
                         'isfound': False,
                         'requestmd5': new_hash.upper()}
        }
    db_insert(data)
    data.clear()