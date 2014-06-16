# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import tempfile
from os import unlink
from os.path import exists, isfile

from dateutil import parser

import envoy
from lib.common.abstracts import AntiVirus


class ClamAV(AntiVirus):

    _engine_path = '/usr/bin/clamscan'
    _update_path = '/usr/bin/freshclam'

    def __init__(self, data):
        AntiVirus.__init__(self, data)
        self.data = data

    @property
    def is_installed(self):
        return isfile(self._engine_path) and isfile(self._update_path)

    @property
    def engine_path(self):
        return self._engine_path

    @property
    def update_path(self):
        return self._update_path

    @property
    def version(self):
        #: Get ClamAV version
        r = envoy.run(self._engine_path + ' --version', timeout=15)
        results = filter(None, r.std_out.split('/'))
        try:
            return dict(engine=results[0].split()[1], definitions=results[1])
        except Exception as e:
            return 'Error: version failed to execute. %s' % e

    # @staticmethod
    # def update_available(self):
    #     """ Check if an update is available.
    #
    #     :return: bool - Update availabe or not.
    #     """
    #     r = envoy.run('sudo ' + self._update_path + ' -c', timeout=15)
    #     results = filter(None, r.std_out.splitlines())
    #     for result in results:
    #         if 'You are currently up-to-date' in result:
    #             return False
    #     return True

    # @staticmethod
    def update_definitions(self):
        """Update ClamAV signatures"""
        # if self.update_available():
        r = envoy.run('sudo ' + self._update_path, timeout=30)
        #: return key, stdout as a dictionary
        results = filter(None, r.std_out.splitlines())
        for result in results:
            if 'Update was successfully completed.' in result:
                return 'Update was successfully completed.'
        return 'Error: update failed to execute.'
        # else:
        #     return 'You are currently up-to-date'

    def format_output(self, output):
        avg_tag = {}
        avg_results = output.split('\n')
        avg_results = filter(None, avg_results)
        avg_tag['av'] = 'ClamAV'
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
            #: Run ClamAV on tmp file
            r = envoy.run('/usr/bin/avgscan ' + name, timeout=15)
            #: delete tmp file
            unlink(name)
            exists(name)
            #: return key, stdout as a dictionary
            return 'ClamAV', self.format_output(r.std_out)
        else:
            return 'ClamAV', dict(error='ClamAV Engine is not installed.')

# myClamAV = ClamAV(None)
# print myClamAV.is_installed
# print myClamAV.version
# print myClamAV.update_definitions()
# print
