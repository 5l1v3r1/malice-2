import os
import ConfigParser
from app.api.metascan_api import MetaScan, Admin

__author__ = 'Josh Maine'

_current_dir = os.path.abspath(os.path.dirname(__file__))
BIT9_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "..", ".."))

config = ConfigParser.ConfigParser()
config.read(os.path.join(BIT9_ROOT, 'conf/config.cfg'))
meta_scan_ip = config.get('Metascan', 'IP')
meta_scan_port = config.get('Metascan', 'Port')

metascan = MetaScan(meta_scan_ip, meta_scan_port)
meta_admin = Admin(meta_scan_ip, meta_scan_port)

# TODO FINISH METASCAN