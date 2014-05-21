# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import os
import ConfigParser
from api.metascan_api import MetaScan, Admin
from lib.common.constants import MALICE_ROOT


conf_path = os.path.normpath(os.path.join(MALICE_ROOT, "conf", "config.cfg"))
config = ConfigParser.ConfigParser()
config.read(conf_path)

meta_scan_ip = config.get('Metascan', 'IP')
meta_scan_port = config.get('Metascan', 'Port')

# metascan = MetaScan(meta_scan_ip, meta_scan_port)
# meta_admin = Admin(meta_scan_ip, meta_scan_port)

# TODO FINISH METASCAN