#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.mod_api.decorators import get_view_rate_limit, ratelimit
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask_wtf.csrf import CsrfProtect

from app import app, db

import hashlib
import rethinkdb as r

from app.scans import single_hash_search, batch_search_hash, scan_upload
from app.views import update_upload_file_metadata
from lib.common.utils import parse_hash_list, list_to_string
from lib.core.database import insert_in_samples_db, update_sample_in_db, is_hash_in_db

__author__ = 'Josh Maine'

try:
    import pydeep
except ImportError:
    pass
try:
    import magic
except ImportError:
    pass

mod_api = Blueprint('api', __name__, url_prefix='/api/v1')
csrf = CsrfProtect(app)

@mod_api.route('/search/file', methods=['GET'])
@ratelimit(limit=300, per=60 * 15)
def search_view():
    arg_hash = request.args['md5']
    hash = parse_hash_list((arg_hash))
    if hash:
        found = single_hash_search(hash)
        if found:
            return jsonify(found), 200
        else:
            return jsonify(dict(error='Not a valid API end point.', response=404)), 404
    else:
        return 'Missing Parameters', 400


@mod_api.route('/search/files', methods=['GET'])
@ratelimit(limit=300, per=60 * 15)
def batch_search_view():
    arg_hash = request.args.getlist('md5')
    hash_list = parse_hash_list(list_to_string(arg_hash))
    if hash_list:
        found = batch_search_hash(hash_list)
        if found:
            return jsonify(results=found), 200
            # return json.dumps(found)
            # return jsonify(json.dumps(found))
        else:
            return jsonify(dict(error='Not a valid API end point.', response=404)), 404
    else:
        return jsonify(dict(error='Missing Parameters', response=400)), 400

@csrf.exempt
@mod_api.route('/file/scan', methods=['POST'])
@ratelimit(limit=300, per=60 * 15)
def upload_view():
    upload_file = request.files['file']
    file_stream = upload_file.stream.read()
    if file_stream:
        #: Collect upload file data
        sample = {'filename': secure_filename(upload_file.filename),
                  'sha1': hashlib.sha1(file_stream).hexdigest().upper(),
                  'sha256': hashlib.sha256(file_stream).hexdigest().upper(),
                  'md5': hashlib.md5(file_stream).hexdigest().upper(),
                  'ssdeep': pydeep.hash_buf(file_stream),
                  'filesize': len(file_stream),
                  'filetype': magic.from_buffer(file_stream),
                  'filemime': upload_file.mimetype,
                  'upload_date': r.now(),
                  'uploaded_by': "api",  # g.user
                  'detection_ratio': dict(infected=0, count=0),
                  'filestatus': "Processing"}
        insert_in_samples_db(sample)
        update_upload_file_metadata(sample)
        #: Run all configured scanners
        sample['detection_ratio'] = scan_upload(file_stream, sample)
        #: Done Processing File
        sample['filestatus'] = 'Complete'
        sample['scancomplete'] = r.now()
        update_sample_in_db(sample)
        found = is_hash_in_db(sample['md5'])
        if found:
            return jsonify(found)
        else:
            return jsonify(dict(error='Not a valid API end point.', response=404)), 404
    else:
        return jsonify(dict(error='Missing Parameters', response=400)), 400

@mod_api.route('/file/report', methods=['GET'])
@ratelimit(limit=300, per=60 * 15)
def report_view():
    pass


@mod_api.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response
