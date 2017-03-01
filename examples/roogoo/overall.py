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
        self.account = self.test_register()

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

    def test_get_url(self, url, name=None, get_key=None):
        with self.client.get(url, name=name, catch_response=True, **self.kwargs) as resp:
            try:
                resp_json = json.loads(resp.text)
                assert resp_json['status'] == 0
                if get_key:
                    return resp_json[get_key]
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
                account['id'] = resp_json['id']
                account['rongyun_id'] = resp_json['rongyun_id']
            except:
                resp.failure("failed to GET /api/v1/my, status_code: {}, msg: {}".format(resp.status_code, resp.text))
                return

        self.test_get_url('/api/v1/users/info')
        self.test_get_url('/api/v1/my/config')

        self.questionnaires()

    def test_register(self):
        try:
            account = {
                'country_code': '852',
                'phone_no': '1%010d' % int(time.time() * 1000000 % (10 ** 10))
            }
            self.register(account)
            # self.logout()
            return account
        except queue.Empty:
            print("Register account data run out !!!")
            exit(0)

    @task(weight=116)
    def test_api_v1_users(self):
        # 11.6k rpm
        self.test_get_url('/api/v1/users?id=&rongyun_id={}'.format(self.account['rongyun_id']), name='/api/v1/users')

    @task(weight=77)
    def test_api_v1_time_lines_list(self):
        # 7.75k rpm
        self.test_get_url('/api/v1/time_lines/list?page=1&page_size=20&type=messages&user_uuid={}'.format(self.account['id']), name='/api/v1/time_lines/list')

    @task(weight=69)
    def test_api_v1_customized_recommendations(self):
        # 6.95k rpm
        self.test_get_url('/api/v1/customized_recommendations?distance=0&gender=2&max_age=99999&min_age=0&online_time=4320&page=1&pagesize=20')

    @task(weight=47)
    def test_api_v1_notifications_unread(self):
        # 4.7k rpm
        self.test_get_url('/api/v1/notifications/unread?version=v2')

    @task(weight=35)
    def test_api_v1_punishments_banned_user_info(self):
        # 3.52k rpm
        self.test_get_url('/api/v1/punishments/banned_user_info?user_uuids%5B%5D={}'.format(self.account['id']), name='banned_user_info')

    @task(weight=32)
    def test_api_v1_my_follow_count(self):
        # 3.24k rpm
        self.test_get_url('/api/v1/my/follow_count')

    @task(weight=27)
    def test_api_v1_users_last_visited_at(self):
        # 2.7k rpm
        self.test_get_url('/api/v1/users/last_visited_at?rongyun_id={}'.format(self.account['rongyun_id']), name='last_visited_at')

    @task(weight=23)
    def test_api_v1_multistage_tests_questionnaire_packages(self):
        # 2.32k rpm
        self.test_get_url('/api/v1/multistage_tests/questionnaire_packages')

    @task(weight=22)
    def test_api_v1_users_tick(self):
        # 2.24k rpm
        self.client.post('/api/v1/users/tick', data='', **self.kwargs)

    @task(weight=19)
    def test_api_v1_my_k_tes_hint(self):
        # 1.88k rpm
        other_user_uuid = 'f4e676c2-b471-40fa-a828-e33439956833'
        self.test_get_url('/api/v1/my/k_tes_hint?other_user_uuid={}'.format(other_user_uuid), name='k_tes_hint')

    @task(weight=18)
    def test_api_v1_black_house_my(self):
        # 1.87k rpm
        self.test_get_url('/api/v1/black_house/my')

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
