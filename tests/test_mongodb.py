#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import unittest
from datetime import datetime

from bson.json_util import dumps
from lib.common.exceptions import MaliceDependencyError
from lib.common.out import print_error, print_info, print_success, print_warning

try:
    import pymongo
except ImportError:
    raise MaliceDependencyError("Unable to import pymongo "
                                "(install with `pip install pymongo`)")


calc_hash = '60B7C0FEAD45F2066E5B805A91F4F0FC'


class MongoDbTestCase(unittest.TestCase):
    def setUp(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['malice']
        try:
            db.create_collection('test')
            # print_success('test database setup completed')
        except pymongo.errors.CollectionInvalid as e:
            print_warning(e)
        finally:
            client.disconnect()

    def tearDown(self):
        client = pymongo.MongoClient('localhost', 27017)
        try:
            db = client.malice
            db.drop_collection('test')
            # print_success('Test collection dropped from database')
        except pymongo.errors.PyMongoError as e:
            print_error(e)
        finally:
            client.disconnect()

    def test_insert(self):
        print_info('Running Insert Test.')
        db = pymongo.MongoClient('localhost', 27017)['malice']

        sample = dict(md5=calc_hash, intel=[], av=[], file=[])
        bit9_data = dict(bit9=dict(threat=0, trust=10))
        sample['intel'].append(bit9_data)

        db.test.insert(sample)

        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))

    def test_remove(self):
        print_info('Running Remove Test.')
        db = pymongo.MongoClient('localhost', 27017)['malice']

        sample = dict(md5=calc_hash, intel=[], av=[], file=[])
        bit9_data = dict(bit9=dict(threat=0, trust=10))
        sample['intel'].append(bit9_data)

        db.test.insert(sample)

        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))

        db.test.remove({'md5': calc_hash})

        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertTrue(found is None)

    def test_update(self):
        print_info('Running Update Test.')
        db = pymongo.MongoClient('localhost', 27017)['malice']

        sample = dict(md5=calc_hash, intel=[], av=[], file=[])

        res = db.test.insert(sample)

        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        bit9_data = dict(bit9=dict(threat=0, trust=10))
        found['intel'].append(bit9_data)

        db.test.save(found)

        # resp = db.test.update({'_id': calc_hash}, {'$addToSet': {"intel": bit9_data}}, upsert=True)
        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))

        vt_data = dict(vt=dict(postive=0, engines=10))
        found['intel'].append(vt_data)

        db.test.save(found)

        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))
        self.assertTrue('vt' in ','.join(module.keys()[0] for module in found['intel']))

        vt_data = dict(vt=dict(postive=9, engines=10))

        for i, module in enumerate(found['intel']):
            if 'vt' in module.keys()[0]:
                found['intel'][i] = vt_data

        db.test.save(found)

        found = db.test.find_one({'md5': calc_hash})
        # print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))
        self.assertTrue('vt' in ','.join(module.keys()[0] for module in found['intel']))
