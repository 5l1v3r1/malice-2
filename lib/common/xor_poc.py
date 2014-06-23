# -*- coding: utf-8 -*-
__author__ = 'http://www.cloudshield.com/blog/advanced-malware/how-to-efficiently-detect-xor-encoded-content-part-1-of-2/'

# Sample usage:	python xor_poc.py –file malicious.doc
# Or: python xor_poc.py –keys 1,2,3,4,5,6,7,8 –string “Try and catch me if you can!”
#     –file malicious.doc

import array
import sys
import binascii
import getopt


def usage():
    print "usage: %s [option] --file [filename]" % sys.argv[0]
    print "-v                   :verbose"
    print "-k|--keys 1,2,4,8    :comma seperated list of key lengths"
    print "-s|--string string   :string to search for"


def xor_delta(s, key_len=1):
    delta = array.array('B', s)

    for x in xrange(key_len, len(s)):
        delta[x - key_len] ^= delta[x]

    # return the delta as a string
    return delta.tostring()[:-key_len]


if __name__ == "__main__":
    search_file = None
    key_lengths = [1, 2, 4, 8]
    search_string = "This program cannot be run in DOS mode."
    verbose = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "k:s:fvh",
                                   ["keys=", "string=", "file="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-k", "--keys"):
            key_lengths = [int(x) for x in a.split(',')]
        elif o in ("-s", "--string"):
            search_string = a
        elif o in ("-f", "--file"):
            search_file = open(a, "r").read()
        elif o == "-v":
            verbose = True
        elif o == "-h":
            usage()
            sys.exit(1)
        else:
            assert False, "unhandled option: %s" % o
    if (search_file == None):
        print "Missing filename"
        usage()
        sys.exit(1)

    for l in key_lengths:
        key_delta = xor_delta(search_string, l)

        if (verbose):
            print "%d:%s" % (l, binascii.hexlify(key_delta))

        doc_delta = xor_delta(search_file, l)

        offset = -1
        while (True):
            offset += 1
            offset = doc_delta.find(key_delta, offset)
            if (offset > 0):
                print ("Key length: %d offset: %08X" % (l, offset))
            else:
                break
