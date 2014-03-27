import itertools
import re

__author__ = 'Josh Maine'


def list_to_string(this_list):
    return ','.join(map(str, this_list))


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


def parse_hash_list(data):
    found_hashes = re.findall('([0-9a-fA-F]{64}|[0-9a-fA-F]{40}|[0-9a-fA-F]{32})', data)
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