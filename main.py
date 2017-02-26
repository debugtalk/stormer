#coding: utf-8
import sys
import argparse
from logger import logger
from locust_start import LocustStarter

def parse_args():
    """ parse command line options.
    """
    parser = argparse.ArgumentParser(
        description='A wrapper for making locustio more convienient to use.')

    parser.add_argument('-f', '--locustfile', dest="locustfile",
                        help="Specify locust file to run test.")
    parser.add_argument('--slaves_num', dest="slaves_num", default='1',
                        help="Specify number of locust slaves.")

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    locustfile = args.locustfile
    if locustfile is None:
        logger.error("locustfile must be specified! use the -f option.")
        sys.exit(0)
    slaves_num = int(args.slaves_num.strip())

    LocustStarter(locustfile=locustfile).start(slaves_num=slaves_num)


if __name__ == '__main__':
    main()
