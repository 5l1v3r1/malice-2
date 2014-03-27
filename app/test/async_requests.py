import ConfigParser
import os
import time

__author__ = 'Josh Maine'

import grequests
import requests
from test_hashes import hash_group
import ujson

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.cfg'))

api_key = config.get('VirusTotal', 'ApiKey')


# Get the scan results for a file.
def get_file_report_linear(this_hash):
    base = 'https://www.virustotal.com/vtapi/v2/'
    params = {'apikey': api_key, 'resource': this_hash}
    return requests.get(base + 'file/report', params=params)


# Get the scan results for a file.
def get_file_report_async(this_hash):
    base = 'https://www.virustotal.com/vtapi/v2/'
    params = {'apikey': api_key, 'resource': this_hash}
    return grequests.get(base + 'file/report', params=params)


def list_to_string(this_list):
    return ','.join(map(str, this_list))

##################################################################################
#: Async Test
start = time.time()
rs = (get_file_report_async(list_to_string(hash_list)) for hash_list in hash_group)
req_list = grequests.map(rs)
print req_list
for req in req_list:
    pass
    # print req.content
end = time.time()
print "Async TIME ++++++++++++++++++++++++++++"
print end - start
#: Linear Test
start = time.time()
for hash_list in hash_group:
    res = get_file_report_linear(list_to_string(hash_list))
    # print res.status_code
    # print res.content
end = time.time()
print "LINEAR TIME +++++++++++++++++++++++++++"
print end - start
