#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'

import sys
import json
import re
import requests


def valid_ip(ip):
    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    return re.match(pattern, ip)


def get_geodata(ip):
    if not valid_ip(ip):
        raise Exception('Invalid IP format')

    return requests.get(url="http://freegeoip.net/json/%s" % ip)


if __name__ == "__main__":
    intput_ip = sys.argv[1]
    geodata = get_geodata(intput_ip)
    print json.dumps(geodata.json(), sort_keys=False, indent=4)
