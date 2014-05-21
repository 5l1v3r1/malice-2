# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from os import unlink
from os.path import exists, isfile
from dateutil import parser
import tempfile
import envoy


# ignore_tags = ['Directory', 'File Name', 'File Permissions', 'File Modification Date/Time']

class AVG():
    def __init__(self, data):
        self.data = data

    @property
    def is_installed(self):
        return isfile('/usr/bin/avgscan')

    def format_output(self, output):
        avg_tag = {}
        avg_results = output.split('\n')
        avg_results = filter(None, avg_results)
        avg_tag['av'] = 'AVG'
        avg_tag['infected'] = '1' in avg_results[11].strip().decode('utf-8')
        avg_tag['infected_string'] = avg_results[6].split()[-1].strip().decode('utf-8')
        tag_part = avg_results[2].split(':', 1)
        engine = tag_part[1].strip().decode('utf-8')
        tag_part = avg_results[3].split(':', 1)
        definitions = parser.parse(tag_part[1].strip().decode('utf-8'))
        # avg_tag['metadata'] = dict(engine=engine, definitions=definitions)
        avg_tag['metadata'] = dict(engine=engine, definitions='Problem')
        # for tag in avg_results:
        #     if 'Virus' in tag:
        #         tag_part = tag.split('Virus')
        #         if len(tag_part) == 2:
        #             avg_tag['infected_string'] = tag_part[1]
        #     tag_part = tag.split(':', 1)
        #     if len(tag_part) == 2:
        #         if 'Infections found' in tag_part[0].strip():
        #             avg_tag['infected'] = '1' in tag_part[1].strip().decode('utf-8')
        #         elif 'database version' in tag_part[0].strip():
        #             avg_tag['engine'] = tag_part[1].strip().decode('utf-8')
        #         elif 'database date' in tag_part[0].strip():
        #             avg_tag['definitions'] = tag_part[1].strip().decode('utf-8')
        #         else:
        #             avg_tag[tag_part[0].strip()] = tag_part[1].strip().decode('utf-8')
        return avg_tag

    def scan(self):
        if self.is_installed:
            #: create tmp file
            handle, name = tempfile.mkstemp(suffix=".data", prefix="avg_")
            #: Write data stream to tmp file
            with open(name, "wb") as f:
                f.write(self.data)
            #: Run exiftool on tmp file
            r = envoy.run('/usr/bin/avgscan ' + name, timeout=15)
            #: delete tmp file
            unlink(name)
            exists(name)
            #: return key, stdout as a dictionary
            return 'AVG', self.format_output(r.std_out)
        else:
            return 'AVG', dict(error='AVG Engine is not installed.')