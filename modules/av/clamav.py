# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from lib.common.abstracts import Signature

class ClamAV(Signature):
    name = "antidbg_devices"
    description = "Checks for the presence of known devices from debuggers and forensic tools"
    severity = 3
    categories = ["anti-debug"]
    authors = ["nex"]
    minimum = "0.5"

    def run(self):
        indicators = [
            ".*SICE$",
            ".*SIWVID$",
            ".*SIWDEBUG$",
            ".*NTICE$",
            ".*REGVXG$",
            ".*FILEVXG$",
            ".*REGSYS$",
            ".*FILEM$",
            ".*TRW$",
            ".*ICEXT$"
        ]

        for indicator in indicators:
            if self.check_file(pattern=indicator, regex=True):
                return True

        return False
