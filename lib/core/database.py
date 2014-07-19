#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from flask import flash, g

from lib.common.exceptions import MaliceDependencyError
from lib.common.out import print_error, print_info, print_success, print_warning
# try:
#     import rethinkdb as r
#     from rethinkdb import RqlRuntimeError
# except ImportError:
#     raise MaliceDependencyError("Unable to import rethinkdb "
#                                 "(install with `pip install rethinkdb`)")
try:
    import pymongo
except ImportError:
    raise MaliceDependencyError("Unable to import pymongo "
                                "(install with `pip install pymongo`)")

# def db_setup():
#     connection = r.connect(host='localhost', port=28015)
#     try:
#         r.db_create('file').run(connection)
#         r.db('file').table_create('files', primary_key='md5').run(connection)
#         print 'file Database setup completed'
#         r.db_create('session').run(connection)
#         r.db('session').table_create('sessions', primary_key='md5').run(connection)
#         print 'session Database setup completed'
#         r.db_create('sample').run(connection)
#         r.db('sample').table_create('samples', primary_key='md5').run(connection)
#         print 'sample Database setup completed'
#     except RqlRuntimeError:
#         print 'Database already exists.'
#     finally:
#         print
#         connection.close()


def db_setup():
    client = pymongo.MongoClient('localhost', 27017)

    db = client['malice']

    try:
        db.create_collection('files')
        print_info('files database setup completed')
    except pymongo.errors.CollectionInvalid as e:
        print_warning(e)
    finally:
        client.disconnect()

    # try:
    #     db.create_collection('session')
    #     print_info('session database setup completed')
    # except pymongo.errors.CollectionInvalid as e:
    #     print_warning(e)
    # finally:
    #     client.disconnect()

    try:
        db.create_collection('samples')
        print_info('samples database setup completed')
    except pymongo.errors.CollectionInvalid as e:
        print_warning(e)
    finally:
        client.disconnect()


# TODO: FIX THIS !!!!!
def db_insert(file_data):
    if is_hash_in_db(file_data['md5']):
        # g.conn.files.update({'_id': file_data['_id']}, file_data)
        try:
            g.conn.files.update({'md5': file_data['md5']}, file_data, upsert=True, multi=False)
            # g.conn.files.update({'_id': file_data['_id']}, {"$set": {'intel': file_data}}, upsert=True, multi=False)
        except pymongo.errors.OperationFailure as e:
            print_error(e)
        # r.table('files').get(file_data['_id']).update(file_data).run(g.rdb_conn)
        # r.table('sessions').get(file_data['_id']).update(file_data).run(g.rdb_sess_conn)
    else:
        try:
            g.conn.files.insert(file_data)
        except pymongo.errors.OperationFailure as e:
            print_error(e)
        # r.table('files').insert(file_data).run(g.rdb_conn)
        # r.table('sessions').insert(file_data).run(g.rdb_sess_conn)
        # TODO : Add flashing back in for files that weren't found.


def is_hash_in_db(this_hash):
    return g.conn.files.find_one({'md5': this_hash})


def insert_in_samples_db(sample):
    try:
        g.conn.samples.insert(sample)
    except pymongo.errors.DuplicateKeyError:
        pass
    # r.table('samples').insert(sample).run(g.rdb_sample_conn)


def update_sample_in_db(sample):
    g.conn.samples.update({'md5': sample['md5']}, sample)
    # r.table('samples').update(sample).run(g.rdb_sample_conn)


def sample_contains_module(sample_id, module_category, is_module_name):
    sample = g.conn.files.find_one({'md5': sample_id})
    return is_module_name in ','.join(module.keys()[0] for module in sample[module_category])

def insert_sample_module(sample_id, module_category, module_name, data):
    if sample_contains_module(sample_id, module_name, module_category):
        update_sample_module(sample_id, module_category, module_name, data)
    else:
        g.conn.files.update({'md5': sample_id}, {'$addToSet': {module_category: data}}, upsert=True)

def update_sample_module(sample_id, module_category, module_name, data):
    found = is_hash_in_db(sample_id)
    for i, module in enumerate(found[module_category]):
        if module_name in module.keys()[0]:
            found[module_category][i] = data
    g.conn.files.save(found)

def destroy_db():
    client = pymongo.MongoClient('localhost', 27017)
    try:
        db = client.malice
        db.drop_collection('files')
        # db.drop_collection('session')
        db.drop_collection('samples')
        print_success("Databases destroyed...you monster!")
        print_info('All containers dropped from database')
    except pymongo.errors.PyMongoError as e:
        print 'Database cannot be killed ... as was prophesized!'
        print_error(e)
    finally:
        client.disconnect()
