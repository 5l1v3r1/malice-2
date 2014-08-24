#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

# Copyright (C) 2010-2014 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import ConfigParser
import os

from lib.common.constants import MALICE_ROOT
from lib.common.exceptions import MaliceOperationalError
from lib.common.objects import Dictionary


class Config:
    """Configuration file parser."""

    def __init__(self, cfg=os.path.join(MALICE_ROOT, "conf", "malice.conf")):
        """@param cfg: configuration file path."""
        self.cfg = cfg
        config = ConfigParser.ConfigParser()
        config.read(cfg)

        for section in config.sections():
            setattr(self, section, Dictionary())
            for name, raw_value in config.items(section):
                try:
                    value = config.getboolean(section, name)
                except ValueError:
                    try:
                        value = config.getint(section, name)
                    except ValueError:
                        value = config.get(section, name)

                setattr(getattr(self, section), name, value)

    def get(self, section):
        """Get option.
        @param section: section to fetch.
        @raise MaliceOperationalError: if section not found.
        @return: option value.
        """
        try:
            return getattr(self, section)
        except AttributeError as e:
            raise MaliceOperationalError("Option %s is not found in "
                                         "configuration, error: %s" %
                                         (section, e))

    def get_enabled(self):
        """Get all enabled options.
        @raise MaliceOperationalError: if nothing found.
        @return: enabled option list.
        """
        enabled_options = []
        config = ConfigParser.ConfigParser()
        config.read(self.cfg)
        try:
            for section in config.sections():
                for name, raw_value in config.items(section):
                    if name == 'enabled' and config.getboolean(section, name):
                        enabled_options.append(section)
        except Exception as e:
            raise MaliceOperationalError(e)
        return enabled_options