import logging
from locust.log import setup_logging
from locust_wrapper.dummy_options import default_options
# setup logging
setup_logging(default_options.loglevel, default_options.logfile)
logger = logging.getLogger(__name__)
