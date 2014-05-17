import os
from os import unlink
from os.path import exists
import tempfile
import envoy

__author__ = 'Josh Maine'


class PDFiD():
    def __init__(self, data):
        self.data = data
        self.path = os.path.join(os.path.dirname(__file__), 'file', 'pdfid.py')

    #: TODO - Fix format output to hangle weird data structure
    def format_output(self, output):
        pdfid_tag = {}
        pdfid_results = output.split('\n')
        pdfid_results = filter(None, pdfid_results)
        for tag in pdfid_results:
            tag_part = tag.split()
            if len(tag_part) == 2:
                pdfid_tag[tag_part[0].lstrip('/')] = tag_part[1].strip().decode('utf-8')
            elif 'PDFiD' in tag_part:
                pdfid_tag['version'] = tag_part[1].strip().decode('utf-8')
            elif 'Header:' in tag_part:
                pdfid_tag['pdf_header'] = tag_part[2].strip().decode('utf-8')
            else:
                pass
        return pdfid_tag

    def scan(self):
        #: create tmp file
        handle, name = tempfile.mkstemp(suffix=".data", prefix="pdfparser_")
        #: Write data stream to tmp file
        with open(name, "wb") as f:
            f.write(self.data)
        #: Run pdfid on tmp file
        r = envoy.run(self.path + ' -a ' + name, timeout=15)
        #: delete tmp file
        unlink(name)
        exists(name)
        #: return key, stdout as a dictionary
        return 'pdfid', self.format_output(r.std_out)
