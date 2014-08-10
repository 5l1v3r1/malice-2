#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from flask import flash, g
from lib.common.exceptions import MaliceDependencyError
from lib.common.out import print_error, print_info, print_success, print_warning

try:
    import pymongo
except ImportError:
    raise MaliceDependencyError("Unable to import pymongo "
                                "(install with `pip install pymongo`)")


def db_setup():
    client = pymongo.MongoClient('localhost', 27017)

    db = client['malice']

    for collection in ['files', 'samples']:
        try:
            db.create_collection(collection)
            print_info(collection + ' database setup completed')
        except pymongo.errors.CollectionInvalid as e:
            print_warning(e)
        finally:
            client.disconnect()


def db_insert(collection, file_data):
    if is_hash_in_db(collection, file_data['md5']):
        # g.mongo.files.update({'_id': file_data['_id']}, file_data)
        try:
            g.mongo[collection].update({'md5': file_data['md5']},
                                       file_data,
                                       upsert=True,
                                       multi=False)
        except pymongo.errors.OperationFailure as e:
            print_error(e)
    else:
        try:
            g.mongo[collection].insert(file_data)
        except pymongo.errors.OperationFailure as e:
            print_error(e)


def is_hash_in_db(collection, this_hash):
    return g.mongo[collection].find_one({'md5': this_hash.upper()})


def insert_in_db(collection, sample):
    try:
        g.mongo[collection].insert(sample)
    except pymongo.errors.DuplicateKeyError:
        pass


def insert_in_samples_db(sample):
    try:
        g.mongo.samples.insert(sample)
    except pymongo.errors.DuplicateKeyError:
        pass
        # r.table('samples').insert(sample).run(g.rdb_sample_conn)


def update_sample_in_db(sample):
    g.mongo.samples.update({'md5': sample['md5']}, sample)
    # r.table('samples').update(sample).run(g.rdb_sample_conn)


def sample_contains_module(sample_id, module_category, is_module_name):
    sample = g.mongo.files.find_one({'md5': sample_id})
    return is_module_name in ','.join(module.keys()[0] for module in sample[module_category])


def insert_sample_module(sample_id, module_category, module_name, data):
    if sample_contains_module(sample_id, module_name, module_category):
        update_sample_module(sample_id, module_category, module_name, data)
    else:
        g.mongo.files.update({'md5': sample_id},
                             {'$addToSet': {module_category: data}},
                             upsert=True)


def update_sample_module(sample_id, module_category, module_name, data):
    found = is_hash_in_db(sample_id)
    for i, module in enumerate(found[module_category]):
        if module_name in module.keys()[0]:
            found[module_category][i] = data
    g.mongo.files.save(found)


def destroy_db():
    client = pymongo.MongoClient('localhost', 27017)
    try:
        db = client.malice
        db.drop_collection('files')
        db.drop_collection('samples')
        print_success("Databases destroyed...you monster!")
        print_info('All containers dropped from database')
    except pymongo.errors.PyMongoError as e:
        print 'Database cannot be killed ... as was prophesized!'
        print_error(e)
    finally:
        client.disconnect()
