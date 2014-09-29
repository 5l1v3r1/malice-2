#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''
import os
import unittest

from app import create_app, db
from app.models import Role, User
from bson.json_util import dumps
from flask import url_for
from lib.common.config import Config
from lib.common.constants import MALICE_ROOT
from lib.common.exceptions import MaliceDependencyError
from lib.common.out import (print_error, print_info, print_success,
                            print_warning)
from lib.common.utils import list_to_string

try:
    import pymongo
except ImportError:
    raise MaliceDependencyError("Unable to import pymongo "
                                "(install with `pip install pymongo`)")

calc_hash = '60B7C0FEAD45F2066E5B805A91F4F0FC'

test_hashes = """60B7C0FEAD45F2066E5B805A91F4F0FC
                 a31691f0078652207ea0b463342b464f
                 5e28284f9b5f9097640d58a73d38ad4c
                 60B7C0FEAD45F2066E5B805A91F4F0FD"""

if os.path.exists(os.path.join(MALICE_ROOT, ".env")):
    print('Importing environment from .env...')
    for line in open(os.path.join(MALICE_ROOT, ".env")):
        var = line.strip().split('=')
        if len(var) == 2 and '#' not in var[0]:
            os.environ[var[0]] = var[1]


def get_modules():
    # modules = ['bit9', 'virustotal', 'shadowserver']
    conf_path = os.path.join(MALICE_ROOT, "conf", "intel.conf")
    if not os.path.exists(conf_path):
        print_error("Configuration file intel.conf not found".format(conf_path))
        intel_options = False
    intel_options = Config(conf_path)
    intel_modules = intel_options.get_enabled()
    return intel_modules

modules = get_modules()
print_info("Running Intel Test for enabled modules: " + list_to_string(modules))


class IntelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)
        client = pymongo.MongoClient('localhost', 27017)
        test_db = client['malice']
        try:
            test_db.create_collection('test')
            # print_success('test database setup completed')
        except pymongo.errors.CollectionInvalid as e:
            print_warning(e)
        finally:
            client.disconnect()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        client = pymongo.MongoClient('localhost', 27017)
        try:
            test_db = client.malice
            test_db.drop_collection('test')
            # print_success('Test collection dropped from database')
        except pymongo.errors.PyMongoError as e:
            print_error(e)
        finally:
            client.disconnect()

    def test_single_hash(self):
        print_info('Running Single Hash Test.')
        response = self.client.post(url_for('malice.intel'),
                                    data=dict(hash=calc_hash),
                                    follow_redirects=True)
        test_db = pymongo.MongoClient('localhost', 27017)['malice']
        found = test_db.files.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertEquals(response.status, "200 OK",
                          "Did not get a 200 Response Status")
        self.assertTrue('teamcymru' in ','.join(module.keys()[0]
                                           for module in found['intel']),
                        "Did not find the teamcymru module in the mongo DB")

        # self.assertTrue(all(module in ','.join(module.keys()[0]
        #                                        for module in found['intel'])
        #                     for module in modules),
        #                 "Not all enabled modules were found in mongo DB")

        # self.assertTrue('calc.exe' in response.get_data(as_text=True),
        #                 "Bit9 Results for calc.exe not being shown in response")

    def test_batch_hash(self):
        print_info('Running Batch Hash Test.')
        response = self.client.post(url_for('malice.intel'),
                                    data=dict(hashes=test_hashes),
                                    follow_redirects=True)
        test_db = pymongo.MongoClient('localhost', 27017)['malice']
        found = test_db.files.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertEquals(response.status, "200 OK",
                          "Did not get a 200 Response Status")
        self.assertTrue('bit9' in ','.join(module.keys()[0]
                                           for module in found['intel']),
                        "Did not find the bit9 module in the mongo DB")
        self.assertTrue(all(module in ','.join(module.keys()[0]
                                               for module in found['intel'])
                            for module in modules),
                        "Not all enabled modules were found in mongo DB")
        self.assertTrue('calc.exe' in response.get_data(as_text=True),
                        "Bit9 Results for calc.exe not being shown in response")


if __name__ == '__main__':
    unittest.main()
