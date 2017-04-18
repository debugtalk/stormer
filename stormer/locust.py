import gevent.monkey; gevent.monkey.patch_all()
import sys
import signal
import multiprocessing
import socket
import gevent
from locust import runners
from locust import events, web
from locust.main import version, load_locustfile
from locust.stats import print_percentile_stats, print_error_report, print_stats
from stormer.base import master_options, slave_options
from stormer.logger import logger

def parse_locustfile(locustfile):
    docstring, locusts = load_locustfile(locustfile)
    locust_classes = locusts.values()
    return locust_classes

def start_master(locust_classes):
    logger.info("Starting web monitor at {}:{}".format(
        master_options.web_host or "*", master_options.port))
    master_greenlet = gevent.spawn(web.start, locust_classes, master_options)
    runners.locust_runner = runners.MasterLocustRunner(locust_classes, master_options)
    try:
        master_greenlet.join()
    except KeyboardInterrupt:
        events.quitting.fire()
        print_stats(runners.locust_runner.request_stats)
        print_percentile_stats(runners.locust_runner.request_stats)
        print_error_report()
        sys.exit(0)

def start_slave(locust_classes):
    runners.locust_runner = runners.SlaveLocustRunner(locust_classes, slave_options)
    slave_greenlet = runners.locust_runner.greenlet
    try:
        slave_greenlet.join()
    except socket.error as ex:
        logger.error("Failed to connect to the Locust master: %s", ex)
        sys.exit(-1)
    except KeyboardInterrupt:
        events.quitting.fire()
        sys.exit(0)


class LocustStarter(object):
    def __init__(self):
        logger.info("Starting Locust %s" % version)

    def start(self, args):
        locust_classes = parse_locustfile(args.locustfile)
        master_options.port = args.port

        if args.slaves_num:
            slaves_num = int(args.slaves_num.strip())
        else:
            slaves_num = multiprocessing.cpu_count()

        for _ in range(slaves_num):
            p_slave = multiprocessing.Process(target=start_slave, args=(locust_classes,))
            p_slave.start()

        try:
            if not args.slave_only:
                master_options.master_host = args.master_host
                p_master = multiprocessing.Process(target=start_master, args=(locust_classes,))
                p_master.start()
                p_master.join()
            else:
                p_slave.join()
        except KeyboardInterrupt:
            sys.exit(0)
