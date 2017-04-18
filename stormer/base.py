import yaml
from stormer.logger import loglevel, logfile

def parse_yaml(yamlfile):
    with open(yamlfile) as stream:
        return yaml.load(stream)


class DummyOptions(object):
    def __init__(self):
        self.host = None
        self.web_host = ""
        self.port = 8089
        self.locustfile = "locustfile"
        self.master = False
        self.slave = False
        self.master_host = "127.0.0.1"
        self.master_port = 5557
        self.master_bind_host = "*"
        self.master_bind_port = 5557
        self.no_web = False
        self.num_clients = 1
        self.hatch_rate = 1
        self.num_requests = None
        self.loglevel = loglevel
        self.logfile = logfile
        self.print_stats = False
        self.only_summary = False
        self.no_reset_stats = False
        self.list_commands = False
        self.show_task_ratio = False
        self.show_task_ratio_json = False
        self.show_version = False

class DummyMasterOptions(DummyOptions):
    def __init__(self):
        super(DummyMasterOptions, self).__init__()
        self.master = True

class DummySlaveOptions(DummyOptions):
    def __init__(self):
        super(DummySlaveOptions, self).__init__()
        self.slave = True

master_options = DummyMasterOptions()
slave_options = DummySlaveOptions()
