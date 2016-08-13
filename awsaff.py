#!/usr/local/bin/python

"""
Script to retrieve product info using Amazon Affiliate API.
"""
from optparse import OptionParser

def get_options():
	parser = OptionParser()
	parser.add_option("-C", "--config_file", dest="filename",
	                  help="Config file name", metavar="FILE")
	parser.add_option("-S", "--strategy", dest="strategy",
	                  help="Specify strategy to follow")

	return parser.parse_args()

def _init_api():
	pass

def main():
	(opt, args) = get_options()

def read_config():
	pass

def get_strategy():
	pass

class Result(object):
	def store(self):
		pass

class Strategy(object):
	def apply(self):
		pass
	def _init():
		pass

if __name__ == "__main__":
	main()