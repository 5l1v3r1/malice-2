#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import itertools
import ntpath
import os
import re
import string
import tempfile
from datetime import datetime

from lib.common.config import Config
from lib.common.constants import MALICE_ROOT

try:
    import chardet
    HAVE_CHARDET = True
except ImportError:
    HAVE_CHARDET = False


def list_to_string(this_list):
    return ','.join(map(str, this_list))


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


def parse_hash_list(data):
    found_hashes = re.findall('((?i)(?<![a-z0-9])[a-fA-F0-9]{32}(?![a-z0-9])|(?i)(?<![a-z0-9])[a-fA-F0-9]{40}(?![a-z0-9])|(?i)(?<![a-z0-9])[a-fA-F0-9]{64}(?![a-z0-9]))', data)
    hash_list = list(set(found_hashes))
    if len(hash_list) == 1:
        return hash_list[0]
    else:
        return hash_list


def hash_type(this_hash):
    if len(this_hash) == 32:
        return 'md5'
    elif len(this_hash) == 40:
        return 'sha1'
    elif len(this_hash) == 64:
        return 'sha256'
    else:
        return None


# TODO : Make this slicker still yo!
def groupby_hash_type(hash_list):
    result = dict()
    for a_hash in hash_list:
        a_hash_type = hash_type(a_hash)
        if a_hash_type is not None:
            result.setdefault(a_hash_type, []).append(a_hash)
    return result


# These functions is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
def to_unicode(s):
    """Attempt to fix non uft-8 string into utf-8. It tries to guess input
    encoding, if fail retry with a replace strategy (so undetectable chars will
    be escaped).  @see: fuller list of encodings at
    http://docs.python.org/library/codecs.html#standard-encodings
    """

    def brute_enc(s2):
        """Trying to decode via simple brute forcing."""
        encodings = ("ascii", "utf8", "latin1")
        for enc in encodings:
            try:
                return unicode(s2, enc)
            except UnicodeDecodeError:
                pass
        return None

    def chardet_enc(s2):
        """Guess encoding via chardet."""
        enc = chardet.detect(s2)["encoding"]

        try:
            return unicode(s2, enc)
        except UnicodeDecodeError:
            pass
        return None

    # If already in unicode, skip.
    if isinstance(s, unicode):
        return s

    # First try to decode against a little set of common encodings.
    result = brute_enc(s)

    # Try via chardet.
    if (not result) and HAVE_CHARDET:
        result = chardet_enc(s)

    # If not possible to convert the input string, try again with
    # a replace strategy.
    if not result:
        result = unicode(s, errors="replace")

    return result


def cleanup_value(v):
    """Cleanup utility function, strips some unwanted parts from values."""
    v = str(v)
    if v.startswith("\\??\\"):
        v = v[4:]
    return v


def sanitize_filename(x):
    """Kind of awful but necessary sanitizing of filenames to
    get rid of unicode problems."""
    out = ""
    for c in x:
        if c in string.letters + string.digits + " _-.":
            out += c
        else:
            out += "_"

    return out


# don't allow all characters in "string.printable", as newlines, carriage
# returns, tabs, \x0b, and \x0c may mess up reports
PRINTABLE_CHARACTERS = string.letters + string.digits + string.punctuation + " \t\r\n"


def convert_char(c):
    """Escapes characters.
    @param c: dirty char.
    @return: sanitized char.
    """
    if c in PRINTABLE_CHARACTERS:
        return c
    else:
        return "\\x%02x" % ord(c)


def is_printable(s):
    """ Test if a string is printable."""
    for c in s:
        if not c in PRINTABLE_CHARACTERS:
            return False
    return True

def convert_to_printable(s):
    """Convert char to printable.
    @param s: string.
    @return: sanitized string.
    """
    if is_printable(s):
        return s
    return "".join(convert_char(c) for c in s)


def datetime_to_iso(timestamp):
    """Parse a datatime string and returns a datetime in iso format.
    @param timestamp: timestamp string
    @return: ISO datetime
    """
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").isoformat()


def get_filename_from_path(path):
    """Cross-platform filename extraction from path.
    @param path: file path.
    @return: filename.
    """
    dirpath, filename = ntpath.split(path)
    return filename if filename else ntpath.basename(dirpath)


def store_temp_file(filedata, filename):
    """Store a temporary file.
    @param filedata: content of the original file.
    @param filename: name of the original file.
    @return: path to the temporary file.
    """
    filename = get_filename_from_path(filename)

    # Reduce length (100 is arbitrary).
    filename = filename[:100]

    options = Config(os.path.join(MALICE_ROOT, "conf", "cuckoo.conf"))
    tmppath = options.cuckoo.tmppath
    targetpath = os.path.join(tmppath, "cuckoo-tmp")
    if not os.path.exists(targetpath):
        os.mkdir(targetpath)

    tmp_dir = tempfile.mkdtemp(prefix="upload_", dir=targetpath)
    tmp_file_path = os.path.join(tmp_dir, filename)
    with open(tmp_file_path, "wb") as tmp_file:
        # If filedata is file object, do chunked copy.
        if hasattr(filedata, "read"):
            chunk = filedata.read(1024)
            while chunk:
                tmp_file.write(chunk)
                chunk = filedata.read(1024)
        else:
            tmp_file.write(filedata)

    return tmp_file_path
