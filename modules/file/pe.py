# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import hashlib
from datetime import datetime
from os import path

from lib.common.abstracts import FileAnalysis
from lib.common.constants import MALICE_ROOT
from lib.common.out import *

# TODO : Reformat and clean up this file and remove Cladio's stuff or give credit
try:
    import pefile

    HAVE_PEFILE = True
except ImportError:
    HAVE_PEFILE = False

try:
    import peutils

    HAVE_PEUTILS = True
except ImportError:
    HAVE_PEUTILS = False

try:
    import magic

    HAVE_MAGIC = True
except ImportError:
    HAVE_MAGIC = False


class PE(FileAnalysis):
    def __init__(self, data):
        FileAnalysis.__init__(self, data)
        # self.data = data
        self.pe = None
        try:
            self.pe = pefile.PE(data=data)
        except pefile.PEFormatError as e:
            print_error("Unable to parse PE file: {0}".format(e))

    def __get_filetype(self, data):
        try:
            file_type = magic.from_buffer(data)
        except Exception:
            return None
        return file_type

    def __md5(self, data):
        return hashlib.md5(data).hexdigest().upper()

    def attributes(self):
        pe_attributes = {
            'optional_header': hex(self.pe.OPTIONAL_HEADER.ImageBase),
            'address_of_entry_point': hex(self.pe.OPTIONAL_HEADER.AddressOfEntryPoint),
            'required_cpu_type': pefile.MACHINE_TYPE[self.pe.FILE_HEADER.Machine],
            'dll': self.pe.is_dll(),
            'exe': self.pe.is_exe(),
            'driver': self.pe.is_driver(),
            # 'checksum': self.pe.generate_checksum(),
            # 'verify_checksum': self.pe.verify_checksum(),
            'subsystem': pefile.SUBSYSTEM_TYPE[self.pe.OPTIONAL_HEADER.Subsystem],
            'compile_time': str(datetime.fromtimestamp(self.pe.FILE_HEADER.TimeDateStamp)),
            'number_of_rva_and_sizes': self.pe.OPTIONAL_HEADER.NumberOfRvaAndSizes
        }
        return pe_attributes

    def imports(self):
        pe_imps = {}
        if hasattr(self.pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
                try:
                    imp = []
                    for symbol in entry.imports:
                        imp.append(dict(address=hex(symbol.address), name=symbol.name))
                    pe_imps[entry.dll] = imp
                except:
                    continue
        return pe_imps

    def imphash(self):
        try:
            imphash = self.pe.get_imphash().upper()
        except AttributeError:
            print_error(
                "No imphash support, upgrade pefile to a version >= 1.2.10-139 (`pip install --upgrade pefile`)")
            return
        return imphash

    def exports(self):
        pe_exps = []
        if hasattr(self.pe, 'DIRECTORY_ENTRY_EXPORT'):
            for symbol in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
                pe_exps.append({'address': hex(self.pe.OPTIONAL_HEADER.ImageBase + symbol.address),
                                'name': symbol.name,
                                'ordinal': symbol.ordinal})
        return pe_exps

    def sections(self):
        pe_sections = []
        for section in self.pe.sections:
            pe_sections.append({'name': section.Name.replace('\x00', ''),
                                'virtual_address': hex(section.VirtualAddress),
                                'virtual_size': hex(section.Misc_VirtualSize),
                                'raw_size': section.SizeOfRawData,
                                'md5': section.get_hash_md5().upper(),
                                'entropy': section.get_entropy()})
        pe_analysis = {
            'number_of_sections': self.pe.FILE_HEADER.NumberOfSections,
            'section_details': pe_sections
        }
        return pe_analysis

    def peid(self):
        pe_matches = dict()
        userdb_file_dir_path = os.path.join(MALICE_ROOT, "data", "UserDB.TXT")
        signatures = peutils.SignatureDatabase(userdb_file_dir_path)
        packer = []
        matches = signatures.match_all(self.pe, ep_only=True)
        if matches:
            map(packer.append, [s[0] for s in matches])
        pe_matches["peid_signature_match"] = packer
        pe_matches["is_probably_packed"] = peutils.is_probably_packed(self.pe)
        pe_matches["is_suspicious"] = peutils.is_suspicious(self.pe)
        pe_matches["is_valid"] = peutils.is_valid(self.pe)
        return pe_matches

    def resources(self):
        resources = []
        if hasattr(self.pe, 'DIRECTORY_ENTRY_RESOURCE'):
            for resource_type in self.pe.DIRECTORY_ENTRY_RESOURCE.entries:
                try:
                    if resource_type.name is not None:
                        name = str(resource_type.name)
                    else:
                        name = str(pefile.RESOURCE_TYPE.get(resource_type.struct.Id))
                    if name is None:
                        name = str(resource_type.struct.Id)

                    if hasattr(resource_type, 'directory'):
                        for resource_id in resource_type.directory.entries:
                            if hasattr(resource_id, 'directory'):
                                for resource_lang in resource_id.directory.entries:
                                    data = self.pe.get_data(resource_lang.data.struct.OffsetToData,
                                                            resource_lang.data.struct.Size)
                                    filetype = self.__get_filetype(data)
                                    md5 = self.__md5(data)
                                    language = pefile.LANG.get(resource_lang.data.lang, None)
                                    sublanguage = pefile.get_sublang_name_for_lang(resource_lang.data.lang,
                                                                                   resource_lang.data.sublang)
                                    offset = ('%-8s' % hex(resource_lang.data.struct.OffsetToData)).strip()
                                    size = ('%-8s' % hex(resource_lang.data.struct.Size)).strip()

                                    resource = {'name': name,
                                                'offset': offset,
                                                'md5': md5,
                                                'size': size,
                                                'filetype': filetype,
                                                'language': language.replace('LANG_', '').lower(),
                                                'sublanguage': sublanguage.replace('SUBLANG_', '').lower()}

                                    # Dump resources if requested to and if the file currently being
                                    # processed is the opened session file.
                                    # This is to avoid that during a --scan all the resources being
                                    # scanned are dumped as well.
                                    # if dump_to and self.pe == self.pe:
                                    #     resource_path = os.path.join(dump_to,
                                    #                                  '{0}_{1}_{2}'.format(__session__.file.md5,
                                    #                                                       offset, name))
                                    #     resource.append(resource_path)
                                    #
                                    #     with open(resource_path, 'wb') as resource_handle:
                                    #         resource_handle.write(data)

                                    resources.append(resource)
                except Exception as e:
                    print_error(e)
                    continue

        return resources

    def scan(self):
        pe = {'attributes': self.attributes(),
              'imports': self.imports(),
              'exports': self.exports(),
              'importhash': self.imphash(),
              'sections': self.sections(),
              'peid': self.peid(),
              'resources': self.resources()}
        return 'pe', pe
