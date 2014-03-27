__author__ = 'Josh Maine'

import re

def parse_hash_list(data):
    found_hashes = re.findall('([0-9a-fA-F]{64}|[0-9a-fA-F]{40}|[0-9a-fA-F]{32})', data)
    return list(set(found_hashes))


def hash_type(this_hash):
    if len(this_hash) == 32:
        return 'md5'
    elif len(this_hash) == 40:
        return 'sha1'
    elif len(this_hash) == 64:
        return 'sha256'
    else:
        return None


# TODO : Make this slicker yo!
def groupby_hash_type(hash_list):
    result = dict()
    for a_hash in hash_list:
        if hash_type(a_hash) == 'md5':
            result.setdefault('md5', []).append(a_hash)
        if hash_type(a_hash) == 'sha1':
            result.setdefault('sha1', []).append(a_hash)
        if hash_type(a_hash) == 'sha256':
            result.setdefault('sha256', []).append(a_hash)
    return result


hash_list = '12602de6659a356141e744bf569e7e56 ' \
            '43367a157685ffbbb557f7cc016dc0b921b7a370,142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e ' \
            '142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e ' \
            'shit balls f29356002df533028467ed7947be1dc4 45cc061d9581e52f008e90e81da2cfd9'
corrected_list = parse_hash_list(hash_list)
for a_hash in corrected_list:
    print "Hash: " + a_hash + " is typeof " + hash_type(a_hash)
hash_group = groupby_hash_type(list(parse_hash_list(hash_list)))
print "Gimme just the md5s:"
for md5 in hash_group['md5']:
    print md5
    