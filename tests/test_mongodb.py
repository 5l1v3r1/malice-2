#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from lib.common.exceptions import MaliceDependencyError
from lib.common.out import print_info, print_warning, print_success, print_error

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''
__reference__ = 'https://github.com/miguelgrinberg/flasky/blob/master/tests/test_user_model.py'

import unittest
import time
from datetime import datetime

try:
    import pymongo
except ImportError:
    raise MaliceDependencyError("Unable to import pymongo "
                                "(install with `pip install pymongo`)")
from bson.json_util import dumps

calc_hash = '60B7C0FEAD45F2066E5B805A91F4F0FC'


class MongoDbTestCase(unittest.TestCase):
    def setUp(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['malice']
        try:
            db.create_collection('test')
            print_success('test database setup completed')
        except pymongo.errors.CollectionInvalid as e:
            print_warning(e)
        finally:
            client.disconnect()

    def tearDown(self):
        client = pymongo.MongoClient('localhost', 27017)
        try:
            db = client.malice
            db.drop_collection('test')
            print_success('Test collection dropped from database')
        except pymongo.errors.PyMongoError as e:
            print_error(e)
        finally:
            client.disconnect()

    def test_insert(self):
        data = dict(_id=calc_hash, intel=[{'Bit9': dict(threat=0, trust=10)}])
        db = pymongo.MongoClient('localhost', 27017)['malice']
        db.test.insert(data)
        found = db.test.find_one({'_id': calc_hash})
        print json.dumps(found, sort_keys=False, indent=4)
        self.assertTrue('Bit9' in list(found['intel'][-1].keys()))

    def test_remove(self):
        pass

    def test_insert_subdocument(self):
        pass

    def test_update(self):
        sample = dict(md5=calc_hash, intel=[], av=[], file=[])

        db = pymongo.MongoClient('localhost', 27017)['malice']

        res = db.test.insert(sample)

        found = db.test.find_one({'md5': calc_hash})
        print dumps(found, sort_keys=False, indent=4)
        bit9_data = dict(bit9=dict(threat=0, trust=10))
        found['intel'].append(bit9_data)
        db.test.save(found)
        # resp = db.test.update({'_id': calc_hash}, {'$addToSet': {"intel": bit9_data}}, upsert=True)
        found = db.test.find_one({'md5': calc_hash})
        print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))
        # self.assertTrue('bit' in ' '.join(engine['_id'] for engine in found['intel']))

        # vt_data = dict(_id='vt', postive=0, engines=10)
        vt_data = dict(vt=dict(postive=0, engines=10))
        found['intel'].append(vt_data)
        db.test.save(found)
        # resp = db.test.update({'_id': calc_hash}, {'$push': {'intel': vt_data}})
        # resp = db.test.update({'_id': calc_hash}, {'$addToSet': {"intel": vt_data}}, upsert=True)
        # resp = db.test.find_and_modify({'_id': calc_hash, 'intel._id': 'bit9'}, {'$set': {"intel.vt": vt_data}}, upsert=True)
        # db.test.update({'_id': calc_hash}, {'$set': intel.}, upsert=True)
        found = db.test.find_one({'md5': calc_hash})
        print dumps(found, sort_keys=False, indent=4)
        # self.assertTrue('vt' in ' '.join(engine['_id'] for engine in found['intel']))
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))
        self.assertTrue('vt' in ','.join(module.keys()[0] for module in found['intel']))
        # self.assertTrue('vt' in found['intel'][-1].keys())

        # vt_data = dict(_id='vt', postive=9, engines=10)
        vt_data = dict(vt=dict(postive=9, engines=10))
        for i, module in enumerate(found['intel']):
            if 'vt' in module.keys()[0]:
                found['intel'][i] = vt_data

        db.test.save(found)
        # resp = db.test.update({'_id': calc_hash}, {'$addToSet': {"intel": vt_data}})
        # resp = db.test.update({'md5': calc_hash, 'intel.$': 'vt'}, {'$set': {"intel.$.vt": vt_data}}, upsert=True)
        # resp = db.test.update({"md5": calc_hash, "intel": "vt"}, {"$set": {"intel.$": vt_data}})
        # db.test.update({'_id': calc_hash, 'intel': 'VT'}, {'$set': {"intel.$": vt_data}}, upsert=True)
        # db.test.update({'_id': calc_hash}, {'$set': intel.}, upsert=True)
        found = db.test.find_one({'md5': calc_hash})
        print dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit9' in ','.join(module.keys()[0] for module in found['intel']))
        self.assertTrue('vt' in ','.join(module.keys()[0] for module in found['intel']))


    def test_update_subdocument(self):
        # TODO : This works but not the way I want it to, I want on function to insert or update an new module result
        bit9_data = dict(_id=calc_hash, intel=[dict(_id='bit9', threat=0, trust=10)])
        db = pymongo.MongoClient('localhost', 27017)['malice']
        resp = db.test.insert(bit9_data)
        print resp
        found = db.test.find_one({'_id': calc_hash})
        print json.dumps(found, sort_keys=False, indent=4)
        self.assertTrue('bit' in ' '.join(engine['_id'] for engine in found['intel']))

        vt_data = dict(_id='vt', postive=0, engines=10)
        # resp = db.test.update({'_id': calc_hash}, {'$push': {'intel': vt_data}})
        resp = db.test.update({'_id': calc_hash}, {'$addToSet': {"intel": vt_data}}, upsert=True)
        # resp = db.test.find_and_modify({'_id': calc_hash, 'intel._id': 'bit9'}, {'$set': {"intel.vt": vt_data}}, upsert=True)
        print resp
        # db.test.update({'_id': calc_hash}, {'$set': intel.}, upsert=True)
        found = db.test.find_one({'_id': calc_hash})
        print json.dumps(found, sort_keys=False, indent=4)
        self.assertTrue('vt' in ' '.join(engine['_id'] for engine in found['intel']))

        vt_data = dict(_id='vt', postive=9, engines=10)
        # resp = db.test.update({'_id': calc_hash}, {'$addToSet': {"intel": vt_data}}, upsert=True)

        resp = db.test.update({'_id': calc_hash, 'intel._id': 'vt'}, {'$set': {"intel.$": vt_data}}, upsert=True)
        # resp = db.test.update({'_id': calc_hash, 'intel._id': 'vt'}, {'$set': {"intel.$": vt_data}}, upsert=True)
        print resp
        # db.test.update({'_id': calc_hash, 'intel': 'VT'}, {'$set': {"intel.$": vt_data}}, upsert=True)
        # db.test.update({'_id': calc_hash}, {'$set': intel.}, upsert=True)
        found = db.test.find_one({'_id': calc_hash})
        print json.dumps(found, sort_keys=False, indent=4)
        self.assertTrue('vt' in ' '.join(engine['_id'] for engine in found['intel']))

# db.collection.find().forEach( function(doc) {
# do {
#     db.collection.update({_id: doc._id,
#                           comments:{$elemMatch:{user:"test",
#                                                 avatar:{$ne:"new_avatar.jpg"}}}},
#                          {$set:{"comments.$.avatar":"new_avatar.jpg"}});
#   } while (db.getPrevError().n != 0);
# })
