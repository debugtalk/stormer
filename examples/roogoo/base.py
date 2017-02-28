import os
import time
import queue
from random import choice
from string import ascii_letters
import hashlib
import hmac


def get_random_str(length):
    return ''.join(choice(ascii_letters) for i in range(length))

def init_user_data_queue():
    user_data_queue = queue.Queue()
    for index in range(1, 10000):
        account = {
            'country_code': '+852',
            'phone_no': '122%08d' % index
        }
        user_data_queue.put_nowait(account)
    return user_data_queue

def create_file(size):
    file_name = "test_file_{}.dat".format(int(time.time()))
    file_path = os.path.abspath(os.path.join(os.curdir, file_name))
    with open(file_path, "w+") as f:
        f.seek(size - 1)
        f.write('\0')
    return file_path

def sign(device_sn, os_platform, app_version):
    content = ''.join([device_sn, os_platform, app_version]).encode('ascii')
    sign_key = "fXlaFBjedO4dGj02".encode('ascii')
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign

if __name__ == '__main__':
    device_sn = '313B6E64-52A0-488E-BDEA-A7412FE971B2'
    os_platform = 'ios'
    app_version = '2.8.3'
    sign(device_sn, os_platform, app_version)
