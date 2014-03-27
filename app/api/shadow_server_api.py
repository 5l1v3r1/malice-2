__author__ = 'Josh Maine'

import requests
import ast

class ShadowServerApi():
    def __init__(self):
        self.shadowserver_bintest = 'http://bin-test.shadowserver.org/api'
        self.shadowserver_av = 'http://innocuous.shadowserver.org/api/'

    def get_shadow_server_bintest(self, this_hash):
        if len(this_hash) == 40:
            params = {'sha1': this_hash}
        else:
            params = {'md5': this_hash}
        response = requests.get(self.shadowserver_bintest, params=params)
        if response.status_code == requests.codes.ok:
            if str(response.content).rstrip().lower() == this_hash.lower() or \
                            str(response.content).rstrip(" {}\n").lower() == this_hash.lower():
                print this_hash + " -- Not Found"
            else:
                print "Manufacturer Name: " + ast.literal_eval(response.content[33:])['mfg_name']
                print "OS Name:           " + ast.literal_eval(response.content[33:])['os_name']
                #print "Description:       " + ast.literal_eval(response.content[33:])['description']
                print "File Name:         " + ast.literal_eval(response.content[33:])['filename']
                #print "Files Version:     " + ast.literal_eval(response.content[33:])['fileversion']
                print "File Time Stamp:   " + ast.literal_eval(response.content[33:])['filetimestamp']
                print
        #print json.dumps(json.loads(response.content[33:]), sort_keys=False, indent=4)
        # resp_json = str(resp.content).lstrip(this_hash.lower() + ' ')
        # print json.dumps(resp_json, sort_keys=True, indent=4, separators=(', ', ': '))
        else:
            print "Server Error Code: " + response.status_code


    def get_shadow_server_av(self, this_hash):
        params = {'query': this_hash}
        response = requests.get(self.shadowserver_av, params=params)
        if response.status_code == requests.codes.ok:
            if str(response.content).rstrip().lower() == this_hash.lower() or \
                            str(response.content).rstrip(" {}\n").lower() == this_hash.lower():
                print this_hash + " -- Not Found"
            else:
                print response.content.strip()
        # resp_json = str(resp.content).lstrip(this_hash.lower() + ' ')
        # print json.dumps(resp_json, sort_keys=True, indent=4, separators=(', ', ': '))
        else:
            print "Server Error Code: " + response.status_code