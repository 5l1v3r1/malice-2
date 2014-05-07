# -*- coding: utf-8 -*-
from flask.ext.login import login_required
from flask_wtf.csrf import CsrfProtect
from werkzeug.utils import secure_filename
from rethinkdb.errors import RqlDriverError
from flask import current_app
import ConfigParser

import os
from app.scans import *
from lib.common.pagination import Pagination
from lib.common.utils import parse_hash_list
from lib.core.database import is_hash_in_db, insert_in_samples_db, update_sample_in_db, db_insert
from app import app
from forms import SearchForm

try:
    import pydeep
except ImportError:
    pass
try:
    import magic
except ImportError:
    pass

try:
    from pybloomfilter import BloomFilter
except ImportError:
    pass

if os.path.isfile('filter.bloom'):
    bf = BloomFilter.open('filter.bloom')
else:
    bf = BloomFilter(10000000, 0.01, 'filter.bloom')

__author__ = 'Josh Maine'

# csrf = CsrfProtect(app)

# config = ConfigParser.SafeConfigParser()
# config.read(os.path.join(app.root_path, '..', 'conf/config.cfg'))
github = 'https://github.com/blacktop/malice' # config.get('SITE', 'Github')

# open connection before each request
@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host='localhost', port=28015, db='file')
        g.rdb_sess_conn = r.connect(host='localhost', port=28015, db='session')
        g.rdb_sample_conn = r.connect(host='localhost', port=28015, db='sample')
    except RqlDriverError:
        abort(503, "Database connection could be established.")


# close the connection after each request
@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
        g.rdb_sess_conn.close()
        g.rdb_sample_conn.close()
    except AttributeError:
        pass


def allowed_file(filename):
    return True
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
# @ldap.login_required
# @login_required
def index():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('home/index.html', form=form, my_github=github)


@app.route('/intel', methods=['GET', 'POST'])
# @ldap.login_required
# @login_required
def intel():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        selection = []
        #: Check if User is using Single Hash Search
        if form.label.data:
            user_hash = parse_hash_list(form.label.data)
            selection.append(single_hash_search(user_hash))
            #: Check if User is using Batch Hash Search
        if form.hashes.data:
            hash_list = parse_hash_list(form.hashes.data)
            if isinstance(hash_list, list):
                selection = batch_search_hash(hash_list)
            else:
                selection.append(single_hash_search(hash_list))
                # return redirect(url_for('intel'))
    # selection = list(r.table('sessions').run(g.rdb_sess_conn))
    # print selection
    # r.table('sessions').delete().run(g.rdb_sess_conn)
    return render_template('intel.html', form=form, searchs=selection, my_github=github)


def update_upload_file_metadata(sample):
    found = is_hash_in_db(sample['md5'])
    if found:
        found['sha1'] = sample['sha1']
        found['sha256'] = sample['sha256']
        found['ssdeep'] = sample['ssdeep']
        found['filesize'] = sample['filesize']
        found['filetype'] = sample['filetype']
        found['filemime'] = sample['filemime']
        upload = {'filename': sample['filename'],
                  'upload_date': sample['upload_date'],
                  'uploaded_by': sample['uploaded_by'],
                  'detection_ratio': sample['detection_ratio']}
        found.setdefault('user_uploads', []).append(upload)
        db_insert(found)
    else:
        file = {'md5': sample['md5'],
                'sha1': sample['sha1'],
                'sha256': sample['sha256'],
                'ssdeep': sample['ssdeep'],
                'filesize': sample['filesize'],
                'filetype': sample['filetype'],
                'filemime': sample['filemime']
        }
        upload = {'filename': sample['filename'],
                  'upload_date': sample['upload_date'],
                  'uploaded_by': sample['uploaded_by'],
                  'detection_ratio': sample['detection_ratio']
        }
        file.setdefault('user_uploads', []).append(upload)
        db_insert(file)


# @csrf.exempt
@app.route('/upload', methods=['POST'])
# @ldap.login_required
# @login_required
def upload():
    form = SearchForm(request.form)
    if request.method == 'POST':
        # TODO: use secure_filename
        for upload_file in request.files.getlist('files[]'):
            file_stream = upload_file.stream.read()
            file_md5 = hashlib.md5(file_stream).hexdigest().upper()
            #: Add file hash to Bloomfilter unless it is already there
            #: Check if user wishes to force a sample rescan
            if file_md5 not in bf or form.force.data:
                bf.add(file_md5)
                #: Collect upload file data
                sample = {'filename': secure_filename(upload_file.filename.encode('utf-8')),
                          'sha1': hashlib.sha1(file_stream).hexdigest().upper(),
                          'sha256': hashlib.sha256(file_stream).hexdigest().upper(),
                          'md5': file_md5,
                          'ssdeep': pydeep.hash_buf(file_stream),
                          'filesize': len(file_stream),
                          'filetype': magic.from_buffer(file_stream),
                          'filemime': upload_file.mimetype,
                          'upload_date': r.now(),
                          'uploaded_by': "jmaine", # g.user
                          'detection_ratio': dict(infected=0, count=0),
                          'filestatus': 'Processing'}
                insert_in_samples_db(sample)
                update_upload_file_metadata(sample)
                #: Run all configured scanners
                sample['detection_ratio'] = scan_upload(file_stream, sample)
                #: Done Processing File
                sample['filestatus'] = 'Complete'
                sample['scancomplete'] = r.now()
                update_sample_in_db(sample)
        #: Once Finished redirect user to the samples page
        return redirect(url_for('samples'))
    return render_template('samples.html')


def parse_sample_data(found):
    av_results = metascan_results = exif = file_metadata = pe = tags = trid = None
    detection_ratio = dict(infected=0, count=0)
    #: Parse out File Metadata
    if 'user_uploads' in found:
        # TODO : Add an analysis_data field for automated rescanning of files
        file_metadata = {'filename': found['user_uploads'][-1]['filename'],
                         'analysis_date': found['user_uploads'][-1]['upload_date'],
                         'first_uploaded': found['user_uploads'][0]['upload_date'],
                         'last_uploaded': found['user_uploads'][-1]['upload_date'],
                         'file_names': ', '.join(name['filename'] for name in found['user_uploads'])}
        #: Parse out Analysis Sections
        for upload in reversed(found['user_uploads']):
            if 'av_results' in upload:
                av_results = upload['av_results']
                for av in av_results:
                    detection_ratio['count'] += 1
                    if av['infected']:
                        detection_ratio['infected'] += 1
                break
        for upload in reversed(found['user_uploads']):
            if 'metascan_results' in upload:
                metascan_results = upload['metascan_results'][-1]['scan_results']['scan_details']
                #: Fix av def update time formatting
                for av in metascan_results:
                    detection_ratio['count'] += 1
                    if metascan_results[av]['scan_result_i'] == 1:
                        detection_ratio['infected'] += 1
                break
        #: Parse out PE Header Info
        if 'pe' in found:
            pe = found['pe']
            pe['attributes']['compile_time'] = parser.parse(pe['attributes']['compile_time'])
        if 'exif' in found and 'File Type' in found['exif']:
            exif = found['exif']
            tags = exif['File Type'].lower()
        #: Parse out TrID
        if 'trid' in found:
            trid = found['trid']
    return av_results, metascan_results, detection_ratio, exif, file_metadata, pe, tags, trid


@app.route('/sample/<id>', methods=['GET', 'POST'])
# @ldap.login_required
# @login_required
def sample(id):
    #: Check sample id is valid hash value
    a_sample_id = parse_hash_list(id)
    if not a_sample_id:
        abort(404)
    #: Check that id exists in DB
    found = is_hash_in_db(a_sample_id)
    if not found:
        abort(404)
    #: Pull out all important information from sample to display to user
    av_results, metascan_results, detection_ratio, exif, file_metadata, pe, tags, trid = parse_sample_data(found)
    return render_template('analysis.html', sample=found, file=file_metadata, tags=tags, pe=pe, exif=exif, trid=trid,
                           av_results=av_results, metascan_results=metascan_results, detection_ratio=detection_ratio)

@app.route('/samples/', defaults={'page': 1})
@app.route('/samples/page/<int:page>', methods=['GET'])
# @ldap.login_required
# @login_required
def samples(page):
    samples_per_page = current_app.config['SAMPLES_PER_PAGE']
    total_sample_count = r.table('samples').count().run(g.rdb_sample_conn)
    if total_sample_count < (page - 1) * samples_per_page or page < 1:
        abort(404)
    skip = (page - 1) * samples_per_page
    if (total_sample_count - skip) > samples_per_page:
        limit = samples_per_page
    else:
        limit = total_sample_count - skip
    # set up the pagination params, set count later
    p = Pagination(total=total_sample_count, per_page=samples_per_page, current_page=page)
    samples = list(r.table('samples').order_by(r.desc('upload_date')).skip(skip).limit(limit).run(g.rdb_sample_conn))

    return render_template('samples.html', samples=samples, per_page=samples_per_page, pagination=p, my_github=github)


@app.route('/system', methods=['GET'])
# @ldap.login_required
@login_required
def system():
    return render_template('system.html', my_github=github)


@app.route('/help', methods=['GET'])
# @ldap.login_required
@login_required
def help():
    url = config.get('SITE', 'Url')
    email = config.get('SITE', 'Email')
    return render_template('help.html', my_url=url, my_email=email, my_github=github)


#: Error Handlers >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.errorhandler(400)
def page_not_found(reason):
    return render_template('error/400.html', reason=reason, my_github=github), 400


@app.errorhandler(404)
def page_not_found(reason):
    return render_template('error/404.html', reason=reason, my_github=github), 404


@app.errorhandler(413)
def page_not_found(reason):
    return render_template('error/413.html', reason=reason, my_github=github), 413


@app.errorhandler(500)
def page_not_found(reason):
    return render_template('error/500.html', reason=reason, my_github=github), 500


# @csrf.error_handler
# def csrf_error(reason):
#     return render_template('error/csrf_error.html', reason=reason, my_github=github), 400


#: Template Filters >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.template_filter('time_from_now')
def time_from_now(this_date):
    pass


@app.template_filter('tail')
def tail_filename(s):
    try:
        if len(s) > 40:
            return '...' + s[-40:]
        else:
            return s
    except:
        return ''


@app.template_filter('percent')
def percent(s):
    return "{0:.0%}".format(s)

#:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# TODO - Display Hashes that Weren't Found
# TODO - Progress Bar
# TODO - handle sha256
# TODO - add push notifications