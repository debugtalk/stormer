import sys
import os
import argparse
from stormer.logger import logger
from stormer.locust import LocustStarter
from stormer import ssh

def main():
    """ parse command line options and run commands.
    """
    parser = argparse.ArgumentParser(
        description='Wrappers for making load test more convienient.')

    subparsers = parser.add_subparsers(help='sub-command help')

    locust_subparser = subparsers.add_parser('locust', help='locust wrapper.',
        description='Start locust master and specified number of slaves with one command.')
    locust_subparser.add_argument('-f', '--locustfile', dest="locustfile",
                                  help="Specify locust file to run test.")
    locust_subparser.add_argument('-P', '--port', '--web-port', dest="port", default='',
                                  help="Port on which to run web host.")
    locust_subparser.add_argument('--slaves_num', dest="slaves_num", default='1',
                                  help="Specify number of locust slaves.")
    locust_subparser.set_defaults(func=main_locust)

    sput_subparser = subparsers.add_parser('sput', help='scp wrapper for putting files.',
        description='Copy local file/directory to remote host with ssh.')
    sput_subparser.add_argument('--hostsfile', dest="hostsfile",
                                help="Specify hosts file to handle.")
    sput_subparser.add_argument('--localpath', dest="localpath",
                                help="Specify localpath of file or directory to transfer.")
    sput_subparser.add_argument('--remotepath', dest="remotepath",
                                help="Specify remotepath of file or directory to transfer.")
    sput_subparser.set_defaults(func=main_sput)

    args = parser.parse_args()
    args.func(args)

    return args

def main_locust(args):
    locustfile = args.locustfile
    if locustfile is None:
        logger.error("locustfile must be specified! use the -f option.")
        sys.exit(0)

    port = args.port.strip()
    port = int(port) if port.isdigit() else None
    slaves_num = int(args.slaves_num.strip())

    LocustStarter().start(locustfile=locustfile.strip(), port=port, slaves_num=slaves_num)

def main_sput(args):
    hostsfile = args.hostsfile
    if hostsfile is None:
        logger.error("hostsfile must be specified! use the --hostsfile option.")
        sys.exit(0)

    localpath = args.localpath
    if localpath is None:
        logger.error("localpath must be specified! use the --localpath option.")
        sys.exit(0)

    remotepath = args.remotepath.strip()
    ssh.sput(hostsfile.strip(), localpath.strip(), remotepath)


if __name__ == '__main__':
    main()
