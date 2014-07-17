#!/usr/bin/env python
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

class Comodo(AntiVirus):
    def __init__(self, data):
        self.data = data

    def format_output(self, output):
        comodo_tag = {}
        comodo_results = output.split('\n')
        comodo_results = filter(None, comodo_results)
        for tag in comodo_results:
            if 'Virus identified' in tag:
                tag_part = tag.split('Virus identified')
                if len(tag_part) == 2:
                    comodo_tag['infected_string'] = tag_part[1]
            tag_part = tag.split(':', 1)
            if len(tag_part) == 2:
                if 'Infections found' in tag_part[0].strip():
                    comodo_tag['infected'] = '1' in tag_part[1]
                comodo_tag[tag_part[0].strip()] = \
                    tag_part[1].strip().decode('utf-8')
        return comodo_tag

    def scan(self):
        #: create tmp file
        handle, name = tempfile.mkstemp(suffix=".data", prefix="comodo_")
        #: Write data stream to tmp file
        with open(name, "wb") as f:
            f.write(self.data)
        #: Run exiftool on tmp file
        r = envoy.run('/usr/bin/comodoscan ' + name, timeout=15)
        #: delete tmp file
        unlink(name)
        exists(name)
        #: return key, stdout as a dictionary
        return 'AVG', self.format_output(r.std_out)
