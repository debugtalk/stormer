import os
import re
import queue
import copy
import time
import json
from requests_toolbelt import MultipartEncoder
from locust import HttpLocust, TaskSet, task
from base import get_random_str, init_user_data_queue, sign

class UserBehavior(TaskSet):
    def on_start(self):
        self.kwargs = {
            'headers': {
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                'User-Agent': 'iOS/2.8.3',
                'Longitude': '113.94755',
                'Latitude':	'22.54023'
            },
            'verify': False
        }
        self.kwargs['headers']['Token'] = self.get_token()

    def get_token(self):
        device_sn = '{}-{}-{}-{}-{}'.format(get_random_str(8), get_random_str(4), get_random_str(4), get_random_str(4), get_random_str(12))
        os_platform = 'ios'
        app_version = '2.8.3'
        signature = sign(device_sn, os_platform, app_version)
        data = "api_version=1&app_datetime=2017-02-28%2012%3A12%3A54%20%2B0800&app_version={app_version}&device_sn={device_sn}&lang=en-CN&latitude=&longitude=&network=WiFi&operator=%E4%B8%AD%E5%9B%BD%E8%81%94%E9%80%9A&os_platform={os_platform}&os_version=10.2.1&sign={signature}".format(
            device_sn=device_sn,
            os_platform=os_platform,
            app_version=app_version,
            signature=signature
        )
        with self.client.post('/api/v1/service_info', data=data, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
                return resp_json['token']
            except:
                resp.failure("failed to get token, status_code: {}, msg: {}".format(resp.status_code, resp.text))

    def test_get_url(self, url, name=None):
        with self.client.get(url, name=name, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
            except:
                resp.failure("failed to GET url: {}, status_code: {}, msg: {}".format(url, resp.status_code, resp.text))

    def send_validate_code(self, account):
        url = '/api/v1/users/send_validate_code'
        data = 'country_code={}&phone_no={}'.format(
            account['country_code'], account['phone_no'])
        with self.client.post(url, data=data, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
            except:
                resp.failure("failed to send_validate_code, status_code: {}, msg: {}".format(resp.status_code, resp.text))
                return

        validate_code = resp_json['register_code']

        url = '/api/v1/users/valid_code'
        data += '&validate_code={}'.format(validate_code)
        with self.client.post(url, data=data, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
            except:
                resp.failure("failed to send_validate_code, status_code: {}, msg: {}".format(resp.status_code, resp.text))
                return

        return validate_code

    def login(self, account):
        self.test_get_url('/api/v1/service_info?app_version=2.8.3&os_platform=ios')
        self.send_validate_code(account)
        self.test_get_url('/api/v1/my')
        self.test_get_url('/api/v1/my/config')
        self.test_get_url('/api/v1/my/config')
        self.test_get_url('/api/v1/customized_recommendations?distance=0&gender=2&max_age=99999&min_age=0&online_time=4320&page=1&pagesize=20')
        self.test_get_url('/api/v1/daily_contents?page=1&page_size=20')
        self.test_get_url('/api/v1/notifications/unread?version=v2')
        self.test_get_url('/api/v1/users/info')
        self.test_get_url(url='/api/v1/punishments/banned_user_info?user_uuids%5B%5D={}'.format(account['uuid']), name='banned_user_info')
        self.test_get_url('/api/v1/punishments')
        self.test_get_url('/api/v1/multistage_tests/delta_questionnaires?detail=0')
        self.test_get_url('/api/v1/black_house/my')
        self.test_get_url('/api/v1/my/recommend_friends?distance=0&gender=2&max_age=200&min_age=0&online_time=4320&page=1')

    def logout(self):
        url = '/api/v1/users/logout'
        with self.client.post(url, data='', catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
                return resp_json
            except:
                resp.failure("failed to logout, msg: {}".format(resp.text))

    def questionnaires(self):
        url = '/api/v1/multistage_tests/questionnaires?questionnaire_package_id=0'
        with self.client.get(url, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
            except:
                resp.failure("failed to get questionnaires, msg: {}".format(resp.text))
                return

        questionnaire_id = resp_json['id']
        data = ""
        scenes = resp_json['scenes']
        for scene in scenes:
            questions = scene['questions']
            for question in questions:
                question_id = question['id']
                options = question['options']
                option_id = options[0]['id']
                data += 'answers%5B%5D%5Bquestion_id%5D={}&answers%5B%5D%5Boption_id%5D={}&'.format(question_id, option_id)

        url = '/api/v1/multistage_tests'
        data += 'questionnaire_id={}'.format(questionnaire_id)
        with self.client.post(url, data=data, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
            except:
                resp.failure("failed to multistage_tests, msg: {}".format(resp.text))

    def post_users(self, account, validate_code):
        kwargs = copy.deepcopy(self.kwargs)
        m = MultipartEncoder(
            fields = {
                'gender': '1',
                'phone_no': account['phone_no'],
                'nick_name': 'test',
                'os_platform': 'ios',
                'birthday': '1988-03-28 08:00:00 +0800',
                'validate_code': validate_code,
                'avatar': ('filename', self.locust.avatar_content, 'image/jpeg'),
                'invitation_code': '',
                'country_code': account['country_code'],
                'want_gender': '0'
            }
        )

        kwargs['headers']['Content-Type'] = m.content_type
        with self.client.post('/api/v1/users', data=m, catch_response=True, **kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
                return True
            except:
                resp.failure("failed to register, status_code: {}, msg: {}".format(resp.status_code, resp.text))
                return False

    def register(self, account):
        self.test_get_url('/api/v1/service_info?app_version=2.8.3&os_platform=ios')
        validate_code = self.send_validate_code(account)
        post_success = self.post_users(account, validate_code)
        if not post_success:
            return

        with self.client.get(url='/api/v1/my', catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
                account['uuid'] = resp_json['id']
                account['rongyun_id'] = resp_json['rongyun_id']
            except:
                resp.failure("failed to GET /api/v1/my, status_code: {}, msg: {}".format(resp.status_code, resp.text))
                return

        self.test_get_url('/api/v1/users/info')
        self.test_get_url('/api/v1/my/config')

        self.questionnaires()

        return account

    @task
    def test_register(self):
        try:
            account = {
                'country_code': '852',
                'phone_no': '1%010d' % int(time.time() * 1000000 % (10 ** 10))
            }
            account = self.register(account)
            # self.logout()
            # self.locust.registered_users_queue.put(account)
        except queue.Empty:
            print("Register account data run out !!!")
            exit(0)

    # @task
    def test_login_and_logout(self):
        try:
            account = self.locust.registered_users_queue.get_nowait()
            self.login(account)
            # self.logout()
            self.locust.registered_users_queue.put_nowait(account)
        except queue.Empty:
            print("Login account data run out !!!")
            time.sleep(5)

class WebsiteUser(HttpLocust):
    # host = 'https://api-test.roogooapp.com'
    host = 'http://118.178.114.239'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    avatar_file = os.path.join(dir_path, 'sky.jpg')
    avatar_content = open(avatar_file, 'rb')
    task_set = UserBehavior
    registered_users_queue = queue.Queue()
    min_wait = 1000
    max_wait = 3000
