#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

from flask import g, flash
from lib.common.exceptions import MaliceDependencyError

try:
    import rethinkdb as r
    from rethinkdb import RqlRuntimeError
except ImportError:
    raise MaliceDependencyError("Unable to import rethinkdb "
                                "(install with `pip install rethinkdb`)")


def db_setup():
    connection = r.connect(host='localhost', port=28015)
    try:
        r.db_create('file').run(connection)
        r.db('file').table_create('files', primary_key='md5').run(connection)
        print 'file Database setup completed'
        r.db_create('session').run(connection)
        r.db('session').table_create('sessions', primary_key='md5').run(connection)
        print 'session Database setup completed'
        r.db_create('sample').run(connection)
        r.db('sample').table_create('samples', primary_key='md5').run(connection)
        print 'sample Database setup completed'
    except RqlRuntimeError:
        print 'Database already exists.'
    finally:
        print
        connection.close()


# TODO: FIX THIS !!!!!
def db_insert(file_data):
    if is_hash_in_db(file_data['md5']):
        r.table('files').get(file_data['md5']).update(file_data).run(g.rdb_conn)
        # r.table('sessions').get(file_data['md5']).update(file_data).run(g.rdb_sess_conn)
    else:
        r.table('files').insert(file_data).run(g.rdb_conn)
        # r.table('sessions').insert(file_data).run(g.rdb_sess_conn)
        # TODO : Add flashing back in for files that weren't found.


def is_hash_in_db(this_hash):
    return r.table('files').get(this_hash.upper()).run(g.rdb_conn)


def insert_in_samples_db(sample):
    r.table('samples').insert(sample).run(g.rdb_sample_conn)


def update_sample_in_db(sample):
    r.table('samples').update(sample).run(g.rdb_sample_conn)


def destroy_db():
    try:
        connection = r.connect(host='localhost', port=28015)
        r.db_drop('file').run(connection)
        r.db_drop('session').run(connection)
        r.db_drop('sample').run(connection)
        print "Databases destroyed...you monster!"
        print
    except RqlRuntimeError:
        print 'Database cannot be killed ... as was prophesized!'
    finally:
        connection.close()