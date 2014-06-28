#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import unittest
import simpleldap
# from flask import Flask, url_for
# from app import create_app, db
# from app.models import User, AnonymousUser, Role, Permission
# import json
# import re
# from base64 import b64encode
# from flask import url_for
# from app import create_app, db
# from app.models import User, Role, Post, Comment


LDAP_SERVER = 'ldap.forumsys.com'
LDAP_PORT = 389 # your port
BIND_DN = "cn=read-only-admin,dc=example,dc=com"
BASE_DN = 'dc=example,dc=com'
BIND_PASSWORD = 'password'


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        pass
        # self.app = create_app('testing')
        # self.app_context = self.app.app_context()
        # self.app_context.push()
        # db.create_all()
        # Role.insert_roles()
        # self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        pass
        # db.session.remove()
        # db.drop_all()
        # self.app_context.pop()

    @staticmethod
    def ldap_fetch(uid=None, name=None, passwd=BIND_PASSWORD):
        try:
            if name is not None and passwd is not None:
                l = simpleldap.Connection(LDAP_SERVER,
                                            port=LDAP_PORT,
                                            dn=BIND_DN,
                                            password=BIND_PASSWORD)
                r = l.search('uid={0}'.format(name), base_dn=BASE_DN)
            else:
                conn = simpleldap.Connection(hostname=LDAP_SERVER, port=LDAP_PORT, dn=BIND_DN, password=BIND_PASSWORD)
                is_valid = conn.authenticate('uid={0},{1}'.format(uid, BASE_DN), 'password')
                r = conn.search('uid={0}'.format(uid), BASE_DN)

            return {
                'name': unicode(r[0]['cn'][0]),
                'id': unicode(r[0]['uid'][0]),
                'mail': unicode(r[0]['mail'][0])
            }
        except Exception as e:
            print e
            return None

    def test_ldap_auth(self):
        ldapres = self.ldap_fetch(uid='riemann', passwd='password')
        self.assertTrue(ldapres['id'] == 'riemann')
        ldapres = self.ldap_fetch(name='riemann', passwd='password')
        self.assertTrue(ldapres['id'] == 'riemann')
        self.assertTrue(ldapres['name'] == u'Bernhard Riemann')
        self.assertTrue(ldapres['mail'] == u'riemann@ldap.forumsys.com')

# if __name__ == '__main__':
#     unittest.main()