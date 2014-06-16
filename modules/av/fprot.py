# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import tempfile
from os import unlink
from os.path import exists

import envoy
from lib.common.abstracts import AntiVirus


# ignore_tags = ['Directory', 'File Name', 'File Permissions', 'File Modification Date/Time']

class F_PROT(AntiVirus):
    def __init__(self, data):
        self.data = data

    def format_output(self, output):
        f_prot_tag = {}
        f_prot_results = output.split('\n')
        f_prot_results = filter(None, f_prot_results)
        for tag in f_prot_results:
            if 'Virus identified' in tag:
                tag_part = tag.split('Virus identified')
                if len(tag_part) == 2:
                    f_prot_tag['infected_string'] = tag_part[1]
            tag_part = tag.split(':', 1)
            if len(tag_part) == 2:
                if 'Infections found' in tag_part[0].strip():
                    f_prot_tag['infected'] = '1' in tag_part[1].strip().decode('utf-8')
                elif 'database version' in tag_part[0].strip():
                    f_prot_tag['engine'] = tag_part[1].strip().decode('utf-8')
                elif 'database date' in tag_part[0].strip():
                    f_prot_tag['definitions'] = tag_part[1].strip().decode('utf-8')
                else:
                    f_prot_tag[tag_part[0].strip()] = tag_part[1].strip().decode('utf-8')
        return f_prot_tag

    def scan(self):
        #: create tmp file
        handle, name = tempfile.mkstemp(suffix=".data", prefix="f_prot_")
        #: Write data stream to tmp file
        with open(name, "wb") as f:
            f.write(self.data)
        #: Run fpscan on tmp file
        r = envoy.run('/usr/local/bin/fpscan -r ' + name, timeout=15)
        #: delete tmp file
        unlink(name)
        exists(name)
        #: return key, stdout as a dictionary
        return 'F-PROT', self.format_output(r.std_out)
