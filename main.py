__author__ = 'jqol'

import argparse
from core import InstaCrawler

parser = argparse.ArgumentParser()
parser.add_argument('username')
parser.add_argument(
    '-o',
    '--output',
    help='Specify output directory, cd/download is the default output dir')
args = parser.parse_args()

crawler = InstaCrawler(args.username)
crawler.refresh_list()



