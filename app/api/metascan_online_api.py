import time
import requests

__author__ = 'Josh Maine'


class MetaScanOnline():
    """ Metascan Online Public API v 2.0

        The Metascan Online Public API allows you to harness the power of our cloud-based multi-scanning technology
        integrated directly into your software solution.

        https://www.metascan-online.com/en/public-api
    """

    def __init__(self, apikey):
        self.base = 'https://api.metascan-online.com/v1/'
        self.apikey = apikey

    def scan_file(self, this_file, filename='', archivepwd='', samplesharing=1):
        """
        Initiate scan request

        On Metascan Online, scan is done asynchronously and each scan request is tracked by data id.

        @param this_file:     Contents of the file for scan	[REQUIRED]
        @param filename:      Name of files to preserve extension during scan and meta data	[RECOMMENDED]
        @param archivepwd:    If submitted file is password protected archive	[OPTIONAL]
        @param samplesharing: This flag is only available to users that have purchased access to private scanning
                                through the Metascan Online API. If '0', scanned files will not be stored or shared
                                by Metascan Online, although hashed results will remain available.	[OPTIONAL]
        @return: data_id	Data ID used for retrieving scan results.
                            Since there are potentially multiple scans for same files when any engine has different
                            definition time or when there is an additional engine, this is identifier for per scan
                            other than per file. (JSON)
        """
        url = self.base + 'file'
        params = dict(apikey=self.apikey, filename=filename, archivepwd=archivepwd, samplesharing=samplesharing)
        files = {'file': (this_file, open(this_file, 'rb'))}
        return requests.post(url=url, files=files, params=params)

    def get_scan_result_from_hash(self, this_hash):
        """
        Retrieve scan reports using data hash.

        @param this_hash: SHA1 or MD5 or SHA256	[REQUIRED]
        @return: scan results (JSON)
        """
        url = self.base + 'hash/' + this_hash
        params = dict(apikey=self.apikey)
        return requests.get(url=url, params=params)

    def get_scan_result_from_data_id(self, data_id):
        """
        Retrieve scan results

        On Metascan Online, scan is done asynchronously and each scan request is tracked by data id.
        Initiating a file scan and retrieving the scan results needs to be done with two separate API calls.
        This request needs to be made multiple times until scan is complete.
        Scan completion can be traced using scan_results.progress_percentage value from the response.

        @param data_id: Get from (Scanning a file)	[REQUIRED]
        @return: sca results (JSON)n
        """
        url = self.base + 'file/' + data_id
        params = dict(apikey=self.apikey)
        return requests.get(url=url, params=params)

    def scan_file_and_get_results(self, this_file):
        response = self.scan_file(this_file, self.apikey)
        data_id = response.json()['data_id']
        while True:
            response = self.get_scan_result_from_data_id(data_id=data_id)
            if response.status_code != requests.codes.ok:
                return response
            if response.json()['scan_results']['progress_percentage'] == 100:
                break
            else:
                time.sleep(3)

        return response
