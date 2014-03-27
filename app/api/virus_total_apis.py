#!/usr/bin/python

"""Simple class to interact with VirusTotal's Public and Private API as well as VirusTotal Intelligence.

The APIs are documented at:
https://www.virustotal.com/en/documentation/public-api/
https://www.virustotal.com/en/documentation/private-api/
https://www.virustotal.com/intelligence/help/automation/

EXAMPLE USAGE:::

from virus_total_apis import PublicApi as vtPubAPI

vt = vtPubAPI(<INSERT_API_KEY_HERE>)
response = vt.get_file_report('44cda81782dc2a346abd7b2285530c5f')
error = vt.handle_response_status_code(response)
if error:
    print error
else:
    print json.dumps(response.json(), sort_keys=False, indent=4)

"""

__author__ = 'Josh Maine'

import requests


class PublicApi():
    """ Whenever you exceed the public API request rate limit a 204 HTTP status code is returned.
     If you try to perform calls to functions for which you do not have the required privileges
     an HTTP Error 403 Forbidden is raised.
    """

    def __init__(self, api_key, proxies=False):
        self.api_key = api_key
        self.base = 'https://www.virustotal.com/vtapi/v2/'
        if proxies:
            self.proxies = {
                "http": proxies['http'],
                "https": proxies['https'],
            }
        else:
            self.proxies = proxies
        self.version = 2

    # Submit a file to be scanned by VirusTotal
    def scan_file(self, this_file):
        params = {'apikey': self.api_key}
        files = {'file': (this_file, open(this_file, 'rb'))}
        return requests.post(self.base + 'file/scan', file=files, params=params)

    # Rescan a previously submitted filed or schedule an scan to be performed in the future.
    def rescan_file(self, this_hash):
        params = {'apikey': self.api_key, 'hash': this_hash}
        return requests.post(self.base + 'file/rescan', params=params)

    # Get the scan results for a file.
    def get_file_report(self, this_hash):
        """ You can also specify a CSV list made up of a combination of hashes and scan_ids
        (up to 4 items with the standard request rate), this allows you to perform a batch
        request with one single call.
        i.e. {'resource': '99017f6eebbac24f351415dd410d522d, 88817f6eebbac24f351415dd410d522d'}.
        """
        params = {'apikey': self.api_key, 'resource': this_hash}
        if self.proxies:
            return requests.get(self.base + 'file/report', params=params, proxies=self.proxies)
        else:
            return requests.get(self.base + 'file/report', params=params)

    # Submit a URL to be scanned by VirusTotal.
    def scan_url(self, this_url):
        params = {'apikey': self.api_key, 'url': this_url}
        return requests.post(self.base + 'url/scan', params=params)

    # Get the scan results for a URL. (can do batch searches like get_file_report
    def get_url_report(self, this_url, scan='0'):
        params = {'apikey': self.api_key, 'resource': this_url, 'scan': scan}
        return requests.get(self.base + 'url/report', params=params)

    # Post a comment on a file or URL.
    def put_comments(self, resource, comment):
        params = {'apikey': self.api_key, 'resource': resource, 'comment': comment}
        return requests.post(self.base + 'comments/put', params=params)

    # Get information about a given IP address.
    def get_ip_report(self, this_ip):
        params = {'apikey': self.api_key, 'ip': this_ip}
        return requests.get(self.base + 'ip-address/report', params=params)

    # Get information about a given domain.
    def get_domain_report(self, this_domain):
        params = {'apikey': self.api_key, 'domain': this_domain}
        return requests.get(self.base + 'domain/report', params=params)

    def handle_response_status_code(self, this_response):
        if this_response.status_code == 203:
            return "ERROR: You exceed the public API request rate limit (4 requests of any nature per minute)"
        if this_response.status_code == 403:
            return "ERROR: You tried to perform calls to functions for which you require a Private API key."
        if this_response.status_code == requests.codes.ok:
            return False


class PrivateApi(PublicApi):
    # Submit a file to be scanned by VirusTotal
    def scan_file(self, this_file, notify_url='', notify_changes_only=''):
        params = {'apikey': self.api_key}
        files = {'file': (this_file, open(this_file, 'rb'))}
        return requests.post(self.base + 'file/scan', file=files, params=params)

    # Get a special URL for submitted files bigger than 32MB.
    def get_upload_url(self):
        params = {'apikey': self.api_key}
        return requests.get(self.base + 'file/scan/upload_url', params=params)
        # response.json()['upload_url']

    # Rescan a previously submitted filed or schedule an scan to be performed in the future.
    def rescan_file(self, this_hash, date='', period='', repeat='', notify_url='', notify_changes_only=''):
        params = {'apikey': self.api_key, 'hash': this_hash}
        return requests.post(self.base + 'file/rescan', params=params)

    # Delete a previously scheduled scan.
    def cancel_rescan_file(self, this_hash):
        params = {'apikey': self.api_key, 'hash': this_hash}
        return requests.post(self.base + 'rescan/delete', params=params)

    # Get the scan results for a file.
    def get_file_report(self, this_hash, allinfo='1'):
        params = {'apikey': self.api_key, 'resource': this_hash, 'allinfo': allinfo}
        return requests.get(self.base + 'file/report', params=params)

    # Get a report about the behaviour of the file in sand boxed environment.
    def get_file_behaviour(self, this_hash):
        params = {'apikey': self.api_key, 'hash': this_hash}
        return requests.get(self.base + 'file/behaviour', params=params)

    # Get a dump of the network traffic generated by the file.
    def get_network_traffic(self, this_hash):
        params = {'apikey': self.api_key, 'hash': this_hash}
        return requests.get(self.base + 'file/network-traffic', params=params)
        # ms = magic.magic_open(magic.MAGIC_NONE)
        # ms.load()
        # return ms.buffer(response.text)

    # Search for samples.
    # https://www.virustotal.com/intelligence/help/file-search/#search-modifiers
    def file_search(self, search_options, offset=300):
        #EXAMPLE: 'type:peexe size:90kb+ positives:5+ behaviour:"taskkill"'
        params = {'apikey': self.api_key, 'query': search_options}
        return requests.get(self.base + 'file/search', params=params)

    # File similarity clusters for a given time frame.
    def get_file_clusters(self, this_date):
        params = {'apikey': self.api_key, 'date': this_date}
        return requests.get(self.base + 'file/clusters', params=params)

    # Get a live feed with the latest files submitted to VirusTotal.
    def get_file_distribution(self, before='', after='', reports='false', limit='1000'):
        params = {'apikey': self.api_key, 'before': before, 'after': after, 'reports': reports, 'limit': limit}
        return requests.get(self.base + 'file/distribution', params=params)

    # Download a file by its hash.
    def get_file(self, this_hash):
        params = {'apikey': self.api_key, 'hash': this_hash}
        return requests.get(self.base + 'file/download', params=params)
        # response.content

    # Submit a URL to be scanned by VirusTotal.
    def scan_url(self, this_url):
        params = {'apikey': self.api_key, 'url': this_url}
        return requests.post(self.base + 'url/scan', params=params)

    # Get the scan results for a URL.
    def get_url_report(self, this_url, scan='0', allinfo='1'):
        params = {'apikey': self.api_key, 'resource': this_url, 'allinfo': allinfo}
        return requests.get(self.base + 'url/report', params=params)

    # Get a live feed with the lastest URLs submitted to VirusTotal.
    def get_url_distribution(self, before='', after='', allinfo=1, limit='1000'):
        params = {'apikey': self.api_key, 'before': before, 'after': after, 'allinfo': allinfo, 'limit': limit}
        return requests.get(self.base + 'url/distribution', params=params)

    # Post a comment on a file or URL.
    def put_comments(self, resource, comment):
        params = {'apikey': self.api_key, 'resource': resource, 'comment': comment}
        return requests.post(self.base + 'comments/put', params=params)

    # Get information about a given IP address.
    def get_ip_report(self, this_ip):
        params = {'apikey': self.api_key, 'ip': this_ip}
        return requests.get(self.base + 'ip-address/report', params=params)

    # Get information about a given domain.
    def get_domain_report(self, this_domain):
        params = {'apikey': self.api_key, 'domain': this_domain}
        return requests.get(self.base + 'domain/report', params=params)

    # Get comments for a file or URL.
    def get_comments(self, resource, before=''):
        params = {'apikey': self.api_key, 'resource': resource}
        return requests.get(self.base + 'comments/get', params=params)


class IntelApi():
    """ To make the best use of your VirusTotal Intelligence account and so, we have exposed some
    VirusTotal Intelligence functionality for programmatic interaction even if you do not have a
    Private Mass API key.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base = 'https://www.virustotal.com/intelligence/'

    # Get the scan results for a file.
    def get_hashes_from_search(self, query, page=None):
        """
        query: a VirusTotal Intelligence search string in accordance with the file search documentation .
        <https://www.virustotal.com/intelligence/help/file-search/>
        page: the next_page property of the results of a previously issued query to this API. This parameter
            should not be provided if it is the very first query to the API, i.e. if we are retrieving the
            first page of results.
        apikey: the API key associated to a VirusTotal Community account with VirusTotal Intelligence privileges.
        """
        params = {'query': query, 'apikey': self.api_key, 'page': page}
        response = requests.get(self.base + 'search/programmatic/', params=params)
        next_page = response.json()['next_page']
        return next_page, response

        # Get the scan results for a file.

    def get_file(self, file_hash, local_filename):
        """
        file_hash: You may use either the md5, sha1 or sha256 hash of the file in order to download it.
        apikey: the API key associated to a VirusTotal Community account with VirusTotal Intelligence privileges.
        """
        params = {'hash': file_hash, 'apikey': self.api_key}
        return requests.get(self.base + 'download/', params=params, stream=True)

    def get_all_file_report_pages(self, query):
        responses = []
        next_page, response = self.get_hashes_from_search(self, query)
        responses.append(response)
        while next_page:
            next_page, response = self.get_hashes_from_search(self, query, next_page)
            responses.append(response)
        return responses

    def save_downloaded_file(self, local_filename):
        with open(local_filename, 'wb') as f:
            for chunk in requests.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
