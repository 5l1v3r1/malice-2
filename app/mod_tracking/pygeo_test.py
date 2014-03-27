#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'

import pygeoip
import geoip2.database
import json

gi = pygeoip.GeoIP('GeoLiteCity.dat', pygeoip.MEMORY_CACHE)
geo_data = gi.record_by_addr('98.248.147.192')
print json.dumps(geo_data, sort_keys=False, indent=4)

reader = geoip2.database.Reader('GeoLite2-City.mmdb')
response = reader.city('98.248.147.192')
print response.city.name