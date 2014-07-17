__author__ = 'Josh Maine'

import sys, dircache, os
# import pyclamav
import pyclamdplus
import colorama
import hashlib
import datetime
# from pymongo import MongoClient

# client = MongoClient()
# db = client['clamdb']

class ClamAV():
    def __init__(self, user='', password=''):
        self.baseurl = "https://services.bit9.com/CyberForensicsService/"
        self.user = user
        self.password = password
        self.flag = {'THREAT_TRUST': 1,
                     'FILE_INFO': 2,
                     'PE_HEADER_METADATA': 4,
                     'CERTIFICATE': 8,
                     'BASE_ALL': 15,
                     'CERTIFICATE_EX': 128,
                     'CATEGORY': 256}
        self.version = '1'
        self.tool = "pythonapi"
        colorama.init(autoreset=True)

    def connect(self):
        try:
            cd = pyclamdplus.ClamdUnixSocket()
            # test if server is reachable
            cd.ping()
        except pyclamdplus.ConnectionError:
            # if failed, test for network socket
            cd = pyclamdplus.ClamdNetworkSocket()
            try:
                cd.ping()
            except pyclamdplus.ConnectionError: raise ValueError('could not connect to clamd server either by unix or network socket')

# def scanfile(file):
#     """ Scan a given file
#     """
#     # Call libclamav thought pyclamav
#     try:
#         ret = pyclamav.scanfile(file)
#     except ValueError, e:
#         print '** A problem as occured :', e, '("' + file + '")'
#         return None
#     except TypeError, e:
#         print '** A problem as occured :', e, '("' + file + '")'
#         return None
#     else:
#         # Check return tupple
#         if ret[0] == 0:
#             print file, 'is not infected'
#             return True
#         elif ret[0] == 1:
#             print os.path.basename(file), 'is infected with', colorama.Fore.RED, ret[1], colorama.Fore.RESET
#             post = {'filename': os.path.basename(file),
#                     'md5': hashlib.md5(open(file).read()).hexdigest(),
#                     'infection': ret[1],
#                     'date': datetime.datetime.utcnow()}
#             return post

p_clam = ClamAV()
p_clam.connect()
p_clam.scan_file()
p_clam.

av_scan = db.av_scans
insertID = av_scan.insert(scanfile(sys.argv[1]))
print insertID
