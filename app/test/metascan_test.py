from lxml import etree
import requests
import xmltodict
import json

__author__ = 'Josh Maine'

base = 'URL'

# Submit a file to be scanned by VirusTotal
def scan_file(this_file):
    params = {'method': 'scan'}
    files = {'file': (this_file, open(this_file, 'rb'))}
    # files = {'file': this_file}
    return requests.post(base, files=files, params=params)

def json_response(response, pretty=True):
    if pretty:
        return json.dumps(xmltodict.parse(response.content), sort_keys=False, indent=4)
    else:
        return json.dumps(xmltodict.parse(response.content))

def dict_response(response):
    data = {}
    root = etree.fromstring(response.content)
    for result in root.xpath('//engine_result'):
        engine_result = {}
        for engine in result.getchildren():
            engine_result[engine.tag]=engine.text
        data.setdefault('av_results', []).append(engine_result)
    return data


response = scan_file('/vagrant/app/worker/av/generic/test/file/evil.pdf')

results = dict_response(response)
json_results = json_response(response)
print json_results
print