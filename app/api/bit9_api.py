__author__ = 'Josh Maine'

import requests
import json
import colorama

# ::Colorama Parameters:: ##########################################
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL


class Bit9Api():
    def __init__(self, user='', password='', proxies=False):
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
        if proxies:
            self.proxies = {
                "http": proxies['http'],
                "https": proxies['https'],
            }
        else:
            self.proxies = proxies
        self.version = '1'
        self.tool = "pythonapi"
        colorama.init(autoreset=True)

    def lookup_usageinfos(self, format="json"):
        url = self.baseurl + self.version + "/usageinfos/lookup." + format
        values = dict(username=self.user, password=self.password, tool=self.tool)
        r = requests.post(url, values)
        self.print_response(r, "")
        return r

    def lookup_md5(self, this_hash, flag=15, format="json"):
        url = self.baseurl + self.version + "/hashinfo/lookup." + format
        values = dict(username=self.user, password=self.password, md5=this_hash, flags=flag, tool="test")
        if self.proxies:
            r = requests.post(url, values, proxies=self.proxies)
        else:
            r = requests.post(url, values)
        # self.print_response(r, this_hash)
        return r

    #: TODO - Handle requests.exceptions.ConnectionError
    def lookup_batch_md5(self, hash_list, flag=15, format="json"):
        url = self.baseurl + self.version + "/hashinfos/lookup." + format
        if self.proxies:
            values = dict(username=self.user, password=self.password, md5=hash_list, flags=flag, proxies=self.proxies,
                          tool="test")
        else:
            values = dict(username=self.user, password=self.password, md5=hash_list, flags=flag,
                          tool="test")
        r = requests.post(url, values)
        # self.print_response(r, "")
        return r

    def lookup_extended(self, this_hash, lookup_type, format):
        url = self.baseurl + self.version + lookup_type + "/lookup." + format
        values = dict(username=self.user, password=self.password, md5=this_hash, tool=self.tool)
        r = requests.post(url, values)
        self.print_response(r, this_hash, lookup_type)
        return r

    def lookup_certificates(self, this_hash, format="json"):
        return self.lookup_extended(this_hash, "/certificates", format)

    def lookup_files(self, this_hash, format="json"):
        return self.lookup_extended(this_hash, "/files", format)

    def lookup_packages(self, this_hash, format="json"):
        return self.lookup_extended(this_hash, "/packages", format)

    def lookup_scanresults(self, this_hash, format="json"):
        return self.lookup_extended(this_hash, "/scanresults", format)

    def print_response(self, this_response, this_hash="", detail=""):
        detail = detail.replace(r'/', "")
        if this_hash:
            this_hash = "Hash: " + this_hash
        else:
            this_hash = "Page"
        if this_response.status_code == 200:
            print json.dumps(this_response.json(), sort_keys=False, indent=4)
        elif this_response.status_code == 400:
            print 'Bad Request: What chu\' talkin\' bout Willis?'
        elif this_response.status_code == 401:
            print(
                colorama.Fore.RED + 'Unauthorized: (' + detail + ') Bad Creds or you asked TOO MUCH!' + colorama.Fore.RESET)
        elif this_response.status_code == 404:
            print(colorama.Fore.CYAN + colorama.Style.BRIGHT + this_hash + ' Not found.' + colorama.Style.RESET_ALL)
        elif this_response.status_code == 500:
            print 'Server Error.'

            # TODO Handle Printing XML Edge Case

# Example Usage #############################################################################
# repper = Bit9Api()

# Win 7 SP1 - calc.exe [ md5:60B7C0FEAD45F2066E5B805A91F4F0FC ]
calc_exe_md5 = "a31691f0078652207ea0b463342b464f"
notepad_exe_md5 = "5e28284f9b5f9097640d58a73d38ad4c"

# Bit9 Basic
#print colorama.Back.BLUE + colorama.Fore.BLACK + ":::::::: What is our Usage? ::::::::" + colorama.Style.RESET_ALL
#repper.lookup_usageinfos()
#print colorama.Back.BLUE + colorama.Fore.BLACK + "::::::: Tell Me All You Know :::::::" + colorama.Style.RESET_ALL

# out = repper.lookup_md5(calc_exe_md5)
#print colorama.Back.BLUE + colorama.Fore.BLACK + ":::::::: Trust Level? ::::::::" + colorama.Style.RESET_ALL
##decrip = out.json()['hashinfo']['peheadermetadata']['description']
#print colorama.Fore.GREEN + colorama.Style.BRIGHT + "\t" + out.json()['hashinfo']['trust'] + colorama.Style.RESET_ALL
#
#out = repper.lookup_md5(notepad_exe_md5)
## Example of how to print out specific info
#if out.status_code == requests.codes.ok:
#    print colorama.Back.BLUE + colorama.Fore.BLACK + ":::::::: What is this file? ::::::::" + colorama.Style.RESET_ALL
#    decrip = out.json()['hashinfo']['peheadermetadata']['description']
#    print colorama.Fore.GREEN + colorama.Style.BRIGHT + "\t" + decrip + colorama.Style.RESET_ALL

# Try a bad hash
# repper.lookup_md5("60B7C0FEAD45F2066E5B805A91F4F0FD")

# Bit9 Extended
# repper.lookup_scanresults(calc_exe_md5)
# repper.lookup_certificates(calc_exe_md5)
# repper.lookup_files(calc_exe_md5)
# repper.lookup_packages(calc_exe_md5)
