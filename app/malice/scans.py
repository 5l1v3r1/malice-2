#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import hashlib
import logging
import os
import datetime
# from dateutil import parser
from flask import current_app, flash, g

# from api.metascan_api import MetaScan
from app.malice.worker.av.avast.scanner import avast_engine
from app.malice.worker.av.avg import scanner as avg_engine
from app.malice.worker.av.avira.scanner import avira_engine
from app.malice.worker.av.bitdefender.scanner import bitdefender_engine
from app.malice.worker.av.clamav.scanner import clamav_engine
from app.malice.worker.av.eset.scanner import eset_engine
from app.malice.worker.av.kaspersky.scanner import kaspersky_engine
from app.malice.worker.av.sophos.scanner import sophos_engine
from app.malice.worker.file.exe.pe import pe
from app.malice.worker.file.exif import exif
from app.malice.worker.file.trid import trid
from modules.intel.bit9 import single_query_bit9, batch_query_bit9
from modules.intel.virustotal import single_query_virustotal, batch_query_virustotal

# from lib.common.config import Config
from lib.common.constants import MALICE_ROOT
from lib.common.exceptions import MaliceDependencyError
from lib.common.out import *
from lib.core.database import db_insert, is_hash_in_db, insert_in_samples_db
from lib.scanworker.file import PickleableFileSample
from modules import av, file, intel

# from app.malice.worker.av.f_prot import scanner as f_prot_engine
# from app.malice.worker.file.doc.pdf import pdfparser, pdfid

# try:
#     import rethinkdb as r
# except ImportError:
#     raise MaliceDependencyError("Unable to import rethinkdb."
#                                 "(install with `pip install rethinkdb`)")
try:
    from redis import Redis
    from rq import Queue
    from rq.decorators import job
except ImportError:
    raise MaliceDependencyError("Unable to import redis."
                                "(install with `pip install redis`)")

q = Queue('low', connection=Redis())

log = logging.getLogger(__name__)


# class ScanManager(object):
#     """Handle Malice scan events."""
#
#     def __init__(self):
#         conf_path = os.path.join(MALICE_ROOT, "conf", "av.conf")
#         if not os.path.exists(conf_path):
#             log.error("Configuration file av.conf not found".format(conf_path))
#             self.av_options = False
#             return
#
#         self.av_options = Config(conf_path)
#
#         conf_path = os.path.join(MALICE_ROOT, "conf", "intel.conf")
#         if not os.path.exists(conf_path):
#             log.error("Configuration file intel.conf not found".format(conf_path))
#             self.intel_options = False
#             return
#
#         self.intel_options = Config(conf_path)
#
#         conf_path = os.path.join(MALICE_ROOT, "conf", "file.conf")
#         if not os.path.exists(conf_path):
#             log.error("Configuration file file.conf not found".format(conf_path))
#             self.file_options = False
#             return
#
#         self.file_options = Config(conf_path)
#
#     def run(self, file_stream, sample):
#             results = {}
#
#             # Exit if options were not loaded.
#             if not self.av_options:
#                 return
#             if not self.intel_options:
#                 return
#             if not self.file_options:
#                 return
#
#             print("<< Now Scanning file: {}  >>>>>>>>>>>>>>>>>>>>>>>"
#                   .format(sample['filename']))
#             # vol = VolatilityAPI(self.memfile, self.osprofile)
#
#             # TODO: improve the load of scan functions.
#             # AntiVirus Engines >>>>>>>>>>>>>>>>>>>>>>>
#             print_info("Scanning with AV workers now.")
#
#             if self.av_options.avast.enabled:
#                 results[av.avast.name] = av.avast.scan()
#             if self.av_options.avg.enabled:
#                 results[avg.name] = avg.scan()
#             if self.av_options.avira.enabled:
#                 results[avira.name] = avira.scan()
#             if self.av_options.bitdefender.enabled:
#                 results[bitdefender.name] = bitdefender.scan()
#             if self.av_options.clamav.enabled:
#                 results[clamav.name] = clamav.scan()
#             if self.av_options.comodo.enabled:
#                 results[comodo.name] = comodo.scan()
#             if self.av_options.eset.enabled:
#                 results[eset.name] = eset.scan()
#             if self.av_options.fprot.enabled:
#                 results[fprot.name] = fprot.scan()
#             if self.av_options.kaspersky.enabled:
#                 results[kaspersky.name] = kaspersky.scan()
#             if self.av_options.metascan.enabled:
#                  results[metascan.name] = \
#                      metascan.scan(ip=self.av_options.metascan.ip,
#                                    port=self.av_options.metascan.port,
#                                    key=self.av_options.metascan.key)
#             if self.av_options.panda.enabled:
#                 results[panda.name] = panda.scan()
#             if self.av_options.sophos.enabled:
#                 results[sophos.name] = sophos.scan()
#             if self.av_options.symantec.enabled:
#                 results[symantec.name] = symantec.scan()
#             if self.av_options.yara.enabled:
#                 results[yara.name] = yara.scan()
#
#             print_success("Malice AV scan Complete.")
#
#             # Intel Engines >>>>>>>>>>>>>>>>>>>>>>>>>>>>
#             print_info("Searching for Intel now.")
#
#             if self.intel_options.bit9.enabled:
#                 results[bit9.name] = bit9.query()
#             if self.intel_options.virustotal.enabled:
#                 results[virustotal.name] = virustotal.query()
#             if self.intel_options.shadowserver.enabled:
#                 results[shadowserver.name] = shadowserver.query()
#             if self.intel_options.teamcymru.enabled:
#                 results[teamcymru.name] = teamcymru.query()
#             if self.intel_options.malwr.enabled:
#                 results[malwr.name] = malwr.query()
#             if self.intel_options.anibus.enabled:
#                 results[anibus.name] = anibus.query()
#             if self.intel_options.totalhash.enabled:
#                 results[totalhash.name] = totalhash.query()
#             if self.intel_options.domaintools.enabled:
#                 results[domaintools.name] = domaintools.query()
#             if self.intel_options.opendns.enabled:
#                 results[opendns.name] = opendns.query()
#             if self.intel_options.urlquery.enabled:
#                 results[urlquery.name] = urlquery.query()
#
#             print_success("Intel Search Complete.")
#
#             # File Analysis Engines >>>>>>>>>>>>>>>>>>>>>>
#             print_info("Performing file analysis now.")
#
#             if self.file_options.office.enabled:
#                 results[office.name] = office.analyze()
#             if self.file_options.pdf.enabled:
#                 results[pdf.name] = pdf.analyze()
#             if self.file_options.elf.enabled:
#                 results[elf.name] = elf.analyze()
#             if self.file_options.pe.enabled:
#                 results[pe.name] = pe.analyze()
#             if self.file_options.dotnet.enabled:
#                 results[dotnet.name] = dotnet.analyze()
#             if self.file_options.macho.enabled:
#                 results[macho.name] = macho.analyze()
#             if self.file_options.java.enabled:
#                 results[java.name] = java.analyze()
#             if self.file_options.android.enabled:
#                 results[android.name] = android.analyze()
#             if self.file_options.javascript.enabled:
#                 results[javascript.name] = javascript.analyze()
#             if self.file_options.swf.enabled:
#                 results[swf.name] = swf.analyze()
#             if self.file_options.php.enabled:
#                 results[php.name] = php.analyze()
#             if self.file_options.html.enabled:
#                 results[html.name] = html.analyze()
#             if self.file_options.trid.enabled:
#                 results[trid.name] = trid.analyze()
#             if self.file_options.exif.enabled:
#                 results[exif.name] = exif.analyze()
#             if self.file_options.yara.enabled:
#                 results[yara.name] = yara.analyze()
#
#             print_success("File Analysis Complete.")
#
#             return results
#
# sm = ScanManager()


# TODO : Make it so that it will scan with every available worker instead of
# TODO (cont) : having to do it explicitly
def scan_upload(file_stream, sample):
    # job = q.enqueue(run_workers, file_stream)
    # print job.result
    print("<< Now Scanning file: {}  >>>>>>>>>>>>>>>>>>>>>>>"
          .format(sample['filename']))
    # print_info("Scanning with MetaScan now.")
    # if run_metascan(file_stream, sample['md5']):
    #     print_success("MetaScan Complete.")
    #: Run the AV workers on the file.
    print_info("Scanning with AV workers now.")
    if run_workers(file_stream):
        print_success("Malice AV scan Complete.")
    print_info("Performing file analysis now.")
    print_item("Scanning with EXIF now.", 1)
    exif_scan(file_stream, sample['md5'])
    print_item("Scanning with TrID now.", 1)
    trid_scan(file_stream, sample['md5'])
    # if file_is_pe(file_stream):
    if True:
        print_item("Scanning with PE Analysis now.", 1)
        pe_scan(file_stream, sample['md5'])
    # if file_is_pdf(file_stream):
    #     #: Run PDF Analysis
    #     pdfparser_scan(file_stream, sample['md5'])
    #     pdfid_scan(file_stream, sample['md5'])
    #: Run Intel workers
    print_item("Searching for Intel now.", 1)
    single_hash_search(sample['md5'])
    print_success("File Analysis Complete.")
    found = is_hash_in_db(sample['md5'])
    return found['user_uploads'][-1]['detection_ratio']


def single_hash_search(this_hash):
    found = is_hash_in_db('files', this_hash)
    if not found:
        #: Run all Intel Workers on hash
        # TODO: Make these async with .delay(this_hash)
        single_query_bit9(this_hash)
        single_query_virustotal(this_hash)
        return is_hash_in_db(this_hash)
    else:  #: Fill in the blanks
        # if 'bit9' not in list(found.keys()):
        modules = [module.keys()[0] for module in found['intel']]
        if 'bit9' not in modules:
            single_query_bit9(this_hash)
        if 'virustotal' not in modules:
            single_query_virustotal(this_hash)
        if found:
            # TODO: handle case where all fields are filled out
            # TODO (cont): (session not updating on first submission)
            insert_in_samples_db(found)
            # r.table('sessions').insert(found).run(g.rdb_sess_conn)
            return found
        else:
            return False


def batch_search_hash(hash_list):
    new_hash_list = []
    search_results = []
    #: Check DB for hashes, if found do not query API
    for a_hash in hash_list:
        found = is_hash_in_db(a_hash)
        if found:
            search_results.append(found)
            insert_in_samples_db(found)
            # r.table('sessions').insert(found).run(g.rdb_sess_conn)
        else:
            new_hash_list.append(a_hash)

    if new_hash_list:
        batch_query_bit9(new_hash_list)
        # batch_query_bit9.delay(new_hash_list)
        batch_query_virustotal(new_hash_list)
        for a_new_hash in new_hash_list:
            found = is_hash_in_db(a_new_hash)
            if found:
                search_results.append(found)
        return search_results
    else:
        return search_results


def scan_to_dict(scan, av_name):
    return dict(av=av_name,
                digest=scan.digest,
                infected=scan.infected,
                infected_string=scan.infected_string,
                metadata=scan.metadata,
                timestamp=datetime.datetime.utcnow())
                # timestamp=r.now())


def avast_scan(this_file):
    my_avast_engine_engine = avast_engine()
    result = my_avast_engine_engine.scan(PickleableFileSample
                                         .string_factory(this_file))
    file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'Avast'))
        if result.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'Avast'))
    db_insert(data)
    return data


def avg_scan(this_file):
    my_avg = avg_engine.AVG(this_file)
    result = my_avg.scan()
    # result = my_avg.scan(PickleableFileSample.string_factory(file))
    if 'error' in result[1]:
        flash(result[1]['error'], 'error')
    else:
        file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
        found = is_hash_in_db(file_md5_hash)
        if found:
            found['user_uploads'][-1].setdefault('av_results', [])\
                .append(result[1])
            if result[1]['infected']:
                found['user_uploads'][-1]['detection_ratio']['infected'] += 1
            found['user_uploads'][-1]['detection_ratio']['count'] += 1
            data = found
        else:
            data = dict(md5=file_md5_hash)
            data['user_uploads'][-1].setdefault('av_results', [])\
                .append(result[1])
        db_insert(data)
        return data


# TODO: metadata contains a element (description) that I should append or replace the infected string with
# TODO: [^cont.] i.e. 'Contains code of the Eicar-Test-Signature virus' vs. 'Eicar-Test-Signature'
def avira_scan(file):
    my_avira_engine = avira_engine()
    result = my_avira_engine.scan(PickleableFileSample.string_factory(file))
    file_md5_hash = hashlib.md5(file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'Avira'))
        if result.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'Avira'))
    db_insert(data)
    return data


def eset_scan(this_file):
    my_eset_engine = eset_engine()
    result = my_eset_engine.scan(PickleableFileSample.string_factory(this_file))
    file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'ESET-NOD32'))
        if result.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'ESET-NOD32'))
    db_insert(data)
    return data


def bitdefender_scan(this_file):
    bitdefender = bitdefender_engine()
    result = bitdefender.scan(PickleableFileSample.string_factory(this_file))
    file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'BitDefender'))
        if result.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(result, 'BitDefender'))
    db_insert(data)
    return data


def clamav_scan(this_file):
    my_clamav_engine = clamav_engine()
    results = my_clamav_engine.scan(PickleableFileSample
                                    .string_factory(this_file))
    file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(results, 'ClamAV'))
        if results.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(results, 'ClamAV'))
    db_insert(data)
    return data


def f_prot_scan(this_file):
    pass
    # my_f_prot = f_prot_engine.F_PROT(this_file)
    # result = my_f_prot.scan()
    # result = my_avg.scan(PickleableFileSample.string_factory(file))
    # file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    # found = is_hash_in_db(file_md5_hash)
    # if found:
    #     found['user_uploads'][-1].setdefault('av_results', []).append(scan_to_dict(result, 'AVG'))
    #     if result.infected:
    #         found['user_uploads'][-1]['detection_ratio']['infected'] += 1
    #     found['user_uploads'][-1]['detection_ratio']['count'] += 1
    #     data = found
    # else:
    #     data = dict(md5=file_md5_hash)
    #     data['user_uploads'][-1].setdefault('av_results', []).append(scan_to_dict(result, 'AVG'))
    # db_insert(data)
    # return data


def kaspersky_scan(this_file):
    my_kaspersky_engine = kaspersky_engine()
    results = my_kaspersky_engine.scan(PickleableFileSample
                                       .string_factory(this_file))
    file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(results, 'Kaspersky'))
        if results.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(results, 'Kaspersky'))
    db_insert(data)
    return data


def sophos_scan(this_file):
    my_sophos = sophos_engine()
    results = my_sophos.scan(PickleableFileSample.string_factory(this_file))
    file_md5_hash = hashlib.md5(this_file).hexdigest().upper()
    found = is_hash_in_db(file_md5_hash)
    if found:
        found['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(results, 'Sophos'))
        if results.infected:
            found['user_uploads'][-1]['detection_ratio']['infected'] += 1
        found['user_uploads'][-1]['detection_ratio']['count'] += 1
        data = found
    else:
        data = dict(md5=file_md5_hash)
        data['user_uploads'][-1].setdefault('av_results', [])\
            .append(scan_to_dict(results, 'Sophos'))
    db_insert(data)
    return data


def exif_scan(file_stream, file_md5):
    this_exif = exif.Exif(file_stream)
    if this_exif:
        key, exif_results = this_exif.scan()
        found = is_hash_in_db(file_md5)
        if found:
            found[key] = exif_results
            data = found
        else:
            data = dict(md5=file_md5)
            data[key] = exif_results
        db_insert(data)
        return data
    else:
        print_error("EXIF Analysis Failed.")


def trid_scan(file_stream, file_md5):
    this_trid = trid.TrID(file_stream)
    if this_trid:
        key, trid_results = this_trid.scan()
        found = is_hash_in_db(file_md5)
        if found:
            found[key] = trid_results
            data = found
        else:
            data = dict(md5=file_md5)
            data[key] = trid_results
        db_insert(data)
        return data
    else:
        print_error("TrID Analysis Failed.")


def pe_scan(this_file, file_md5):
    this_pe = pe.PE(this_file)
    if this_pe.pe:
        key, pe_results = this_pe.scan()
        found = is_hash_in_db(file_md5)
        if found:
            found[key] = pe_results
            data = found
        else:
            data = dict(md5=file_md5)
            data[key] = pe_results
        db_insert(data)
        return data
    else:
        print_error("PE Analysis Failed - "
                    "This file might not be a PE Executable.")


# def run_metascan(this_file, file_md5):
#     # TODO : remove these hardcoded creds
#     if config.has_section('Metascan'):
#         meta_scan = MetaScan(ip=config.get('Metascan', 'IP'),
#                              port=config.get('Metascan', 'Port'))
#     else:
#         meta_scan = MetaScan(ip='127.0.0.1', port='8008')
#     if meta_scan.connected:
#         results = meta_scan.scan_file_stream_and_get_results(this_file)
#         if results.status_code != 200:
#             print_error("MetaScan can not be reached.")
#             return None
#         metascan_results = results.json()
#         #: Calculate AV Detection Ratio
#         detection_ratio = dict(infected=0, count=0)
#         for av in metascan_results[u'scan_results'][u'scan_details']:
#             metascan_results[u'scan_results'][u'scan_details'][av][u'def_time'] \
#                 = parser.parse(metascan_results[u'scan_results']
#                                [u'scan_details'][av][u'def_time'])
#             detection_ratio['count'] += 1
#             if metascan_results[u'scan_results'][u'scan_details'][av]['scan_result_i'] == 1:
#                 detection_ratio['infected'] += 1
#         found = is_hash_in_db(file_md5)
#         if found:
#             found['user_uploads'][-1].setdefault('metascan_results', [])\
#                 .append(metascan_results)
#             found['user_uploads'][-1]['detection_ratio']['infected'] += \
#                 detection_ratio['infected']
#             found['user_uploads'][-1]['detection_ratio']['count'] += \
#                 detection_ratio['count']
#             data = found
#         else:
#             data = dict(md5=file_md5)
#             data['user_uploads'][-1].setdefault('metascan_results', [])\
#                 .append(metascan_results)
#         db_insert(data)
#         return metascan_results
#     else:
#         return None


@job('low', connection=Redis(), timeout=50)
def run_workers(file_stream):
    # TODO : Automate this so it will scan all registered engines
    # get_file_details(file_stream)
    # pe_info_results = pe_scan(file_stream)
    # print_item("Scanning with Avast.", 1)
    # avast_scan(file_stream)
    print_item("Scanning with AVG.", 1)
    avg_scan(file_stream)
    # print_item("Scanning with F-PROT.", 1)
    # f_prot_scan(file_stream)
    # print_item("Scanning with Avira.", 1)
    # avira_scan(file_stream)
    # print_item("Scanning with BitDefender.", 1)
    # bitdefender_scan(file_stream)
    print_item("Scanning with ClamAV.", 1)
    clamav_scan(file_stream)
    # print_item("Scanning with ESET.", 1)
    # eset_scan(file_stream)
    # print_item("Scanning with Kaspersky.", 1)
    # kaspersky_scan(file_stream)
    # print_item("Scanning with Sophos.", 1)
    # sophos_scan(file_stream)
    return True
