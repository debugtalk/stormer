import logging
from locust.log import setup_logging

# setup logging
loglevel = 'INFO'
logfile = None

setup_logging(loglevel, logfile)
logger = logging.getLogger(__name__)
