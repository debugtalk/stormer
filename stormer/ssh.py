import os
import time
import paramiko
import threading
from stormer.logger import logger
from stormer import base

class SSHConnector(paramiko.SSHClient):

    def __init__(self, host):
        super(SSHConnector, self).__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(**host)
        self.sftp = self.open_sftp()
        logger.info("Connected to {}:{} with {}".format(
            host['hostname'], host['port'], host['username']))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.sftp.close()
        self.close()

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.exec_command(cmd)
        return stdout.readlines()

    def create_remote_dir(self, remote_dir):
        cmd_create_dir = 'mkdir -p {}'.format(remote_dir)
        self.exec_cmd(cmd_create_dir)
        time.sleep(0.5)

    def get_file(self, remotefile, localfile):
        self.sftp.get(remotefile, localfile)

    def get_dir(self, remote_dir, local_dir):
        pass

    def put_file(self, localfile, remotefile):
        remote_dirpath = os.path.dirname(remotefile)
        if remote_dirpath == '':
            remotefile = os.path.join('~', remotefile)
        else:
            cmd_check_dir = 'test -d {} && echo "ISDIR" || echo "NOTDIR"'.format(remote_dirpath)
            output = self.exec_cmd(cmd_check_dir)
            if output and 'NOTDIR' in output[0]:
                self.create_remote_dir(remote_dirpath)

        logger.info('transfer {} to {}'.format(localfile, remotefile))
        self.sftp.put(localfile, remotefile)

    def __get_all_files_in_local_dir(self, local_dir):
        all_files = list()
        files = os.listdir(local_dir)
        for filename in files:
            path = os.path.join(local_dir, filename)
            if os.path.isdir(path):
                all_files.extend(self.__get_all_files_in_local_dir(path))
            else:
                all_files.append(path)
        return all_files

    def put_dir(self, local_dir, remote_dir):
        """ transfer all file in local_dir to remote_dir.
        """
        all_files = self.__get_all_files_in_local_dir(local_dir)
        for localfile in all_files:
            relative_path = localfile[len(local_dir) + 1:]
            remotefile = os.path.join(remote_dir, relative_path)
            remote_file_dir = os.path.dirname(remotefile)
            self.create_remote_dir(remote_file_dir)
            self.put_file(localfile, remotefile)


def sput(hostsfile, localpath, remotepath):

    def _put_file(host, localfile, remotefile):
        with SSHConnector(host) as ssh_client:
            ssh_client.put_file(localfile, remotefile)

    def _put_dir(host, local_dir, remote_dir):
        with SSHConnector(host) as ssh_client:
            ssh_client.put_dir(local_dir, remote_dir)

    host_list = base.parse_yaml(hostsfile)
    localpath = os.path.abspath(localpath)
    target_func = _put_dir if os.path.isdir(localpath) else _put_file

    for host in host_list:
        threading.Thread(target=target_func, args=(host, localpath, remotepath)).start()
