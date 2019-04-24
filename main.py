__author__ = 'jqol'

import argparse
from core import InstaCrawler, set_download_dir

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument(
        '-o',
        '--output',
        help='Specify output directory, cd/download is the default output dir')
    args = parser.parse_args()
    if args.output is not None:
        set_download_dir(args.output)

    crawler = InstaCrawler(args.username)
    crawler.refresh_list()

    
if __name__ == '__main__':
    main()
