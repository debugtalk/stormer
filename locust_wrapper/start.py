import sys
import signal
from multiprocessing import Process
import socket
import gevent
from locust import runners
from locust import events, web
from locust.main import version, load_locustfile
from locust_wrapper.dummy_options import master_options, slave_options
from locust_wrapper.logger import logger


def parse_locustfile(locustfile):
    docstring, locusts = load_locustfile(locustfile)
    locust_classes = locusts.values()
    return locust_classes

def shutdown(code=0):
    """
    Shut down locust by firing quitting event
    """
    logger.info("Shutting down (exit code %s), bye." % code)
    events.quitting.fire()
    sys.exit(code)

def run(main_greenlet):
    # install SIGTERM handler
    def sig_term_handler():
        logger.info("Got SIGTERM signal")
        shutdown(0)
    gevent.signal(signal.SIGTERM, sig_term_handler)

    try:
        main_greenlet.join()
        code = 0
        if len(runners.locust_runner.errors):
            code = 1
        shutdown(code=code)
    except KeyboardInterrupt:
        shutdown(0)

def start_master(locust_classes):
    logger.info("Starting web monitor at {}:{}".format(
        master_options.web_host or "*", master_options.port))
    main_greenlet = gevent.spawn(web.start, locust_classes, master_options)
    runners.locust_runner = runners.MasterLocustRunner(locust_classes, master_options)
    run(main_greenlet)

def start_slave(locust_classes):
    try:
        runners.locust_runner = runners.SlaveLocustRunner(locust_classes, slave_options)
        main_greenlet = runners.locust_runner.greenlet
        run(main_greenlet)
    except socket.error as ex:
        logger.error("Failed to connect to the Locust master: %s", ex)
        sys.exit(-1)


class LocustStarter(object):
    def __init__(self):
        logger.info("Starting Locust %s" % version)

    def start(self, locustfile, slaves_num=1):
        locust_classes = parse_locustfile(locustfile)

        p_master = Process(target=start_master, args=(locust_classes,))
        p_master.start()

        for _ in range(slaves_num):
            p_slave = Process(target=start_slave, args=(locust_classes,))
            p_slave.start()

        try:
            p_master.join()
        except KeyboardInterrupt:
            pass
