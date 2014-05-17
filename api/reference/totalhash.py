#!/usr/bin/python

import sys
import optparse
import ConfigParser
import hmac
import urllib2
from hashlib import sha256
from xml.dom import minidom

def getCreds():
	config = ConfigParser.RawConfigParser()
	config.read('config.cfg')
	username = config.get('totalhash','username')
	apikey = config.get('totalhash','apikey')
	return username, apikey
	
def totalHash_search(search,num):
	username, apikey = getCreds()
	h = hmac.new(apikey,search,sha256)
	url = "http://api.totalhash.com/search/"+search+"&id="+username+"&sign="+h.hexdigest()+"&start="+str(num)
	page = urllib2.urlopen(url)
			
	xmldoc = minidom.parse(page)
	for num in xmldoc.getElementsByTagName('result'):
		print '************** Total number of results ' + num.getAttribute('numFound') + ' **************'
	for hash in xmldoc.getElementsByTagName('str'):
		print '[+] Hash found: ' + hash.firstChild.nodeValue	
		
	#print h.hexdigest()

def readConfig(args):
	usage = "Usage: python %prog [options] "
	parser = optparse.OptionParser(usage=usage)
	parser.add_option('--av',  '-a', action='store', default=None, help='AV Detection Lookup')
	parser.add_option('--dns', '-d', action='store', default=None, help='DNS Lookup')
	parser.add_option('--email', '-e', action='store', default=None, help='Email Lookup')
	parser.add_option('--filename', '-f', action='store', default=None, help='File Lookup')
	parser.add_option('--hash', '-H', action='store', default=None, help='Hash Lookup')
	parser.add_option('--ip', '-i', action='store', default=None, help='IP Lookup')
	parser.add_option('--mutex', '-m', action='store', default=None, help='Mutex Lookup')
	parser.add_option('--pdb', '-p', action='store', default=None, help='PDB Lookup')
	parser.add_option('--registry', '-r', action='store', default=None, help='Registry Lookup')
	parser.add_option('--url', '-u', action='store', default=None, help='URL Lookup')
	parser.add_option('--useragent', '-U', action='store', default=None, help='User-Agent Lookup')
	parser.add_option('--version', '-v', action='store', default=None, help='Version Lookup')
	parser.add_option('--num', '-n', action='store', default=None, help='Result Index')
	
	global options
	(options,dns) = parser.parse_args(args) 

def main(args):
	readConfig(args)
	if options.av:
		if options.num:
			totalHash_search('av:' + options.av, options.num)
		else:
			totalHash_search('av:' + options.av, 0)
	if options.hash:
		if options.num:
			totalHash_search('hash:' + options.hash, options.num)
		else:
			totalHash_search('hash:' + options.hash, 0)
	if options.mutex:
		if options.num:
			totalHash_search('mutex:' + options.mutex, options.num)
		else:
			totalHash_search('mutex:' + options.mutex, 0)
	if options.dns:
		if options.num:
			totalHash_search('dnsrr:', options.dns, options.num)
		else:
			totalHash_search('dnsrr:' + options.dns, 0)
	if options.email:
		if options.num:
			totalHash_search('email:' + options.email, options.num)
		else:
			totalHash_search('email:' + options.email, 0)
	if options.filename:
		if options.num:
			totalHash_search('filename:' + options.filename, options.num)
		else:
			totalHash_search('filename:' + options.filename, 0)
	if options.pdb:
		if options.num:
			totalHash_search('pdb:' + options.pdb, options.num)
		else:
			totalHash_search('pdb:' + options.pdb, 0)
	if options.registry:
		if options.num:
			totalHash_search('registry:' + options.registry, options.num)
		else:
			totalHash_search('registry:' + options.registry, 0)
	if options.version:
		if options.num:
			totalHash_search('version:' + options.version, options.num)
		else:
			totalHash_search('version:' + options.version, 0)
	if options.ip:
		if options.mum:
			totalHash_search('ip:' + options.ip, options.num)
		else:
			totalHash_search('ip:' + options.ip, 0)
	if options.url:
		if options.num:
			totalHash_search('url:' + options.url, options.num)
		else:
			totalHash_search('url:' + options.url, 0)
	if options.useragent:
		if options.num:
			totalHash_search('useragent:' + options.useragent, options.num)
		else:
			totalHash_search('useragent:' + options.useragent, 0)
	 		
if __name__ == "__main__":
	args = sys.argv[1:]
	if args:
		main(args)
	else:
		print "See help (-h) for details"
		sys.exit(0)

