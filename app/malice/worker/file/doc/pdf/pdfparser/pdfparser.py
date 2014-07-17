import os
from os import unlink
from os.path import exists
import tempfile
import envoy

__author__ = 'Josh Maine'

keywords = ['PDF Comment ', 'Type: ', 'Contains stream', 'Referencing: ']
tokens = ['endobj', 'startxref', 'trailer', 'xref', 'obj']
format_words = ['<<', '>>', '<', '>']

class PdfParser():
    def __init__(self, data):
        self.data = data
        self.path = os.path.join(os.path.dirname(__file__), 'file', 'pdf-parser.py')

    #: TODO - Fix format output to hangle weird data structure
    def format_output(self, output):
        pdfpar_tag = {}
        pdfpar_results = output.split('\n')
        pdfpar_results = filter(None, pdfpar_results)
        for tag in pdfpar_results:
            tag_part = tag.split(':', 1)
            if len(tag_part) == 2:
                pdfpar_tag[tag_part[0].strip()] = tag_part[1].strip().decode('utf-8')
        return pdfpar_tag

    def scan(self):
        #: create tmp file
        handle, name = tempfile.mkstemp(suffix=".data", prefix="pdfparser_")
        #: Write data stream to tmp file
        with open(name, "wb") as f:
            f.write(self.data)
        #: Run pdf-parser.py on tmp file
        r = envoy.run(self.path + ' -v ' + name, timeout=15)
        #: delete tmp file
        unlink(name)
        exists(name)
        #: return key, stdout as a dictionary
        return 'pdfparser', self.format_output(r.std_out)
