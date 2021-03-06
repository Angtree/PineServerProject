import json

from django.test.client import Client
from django.conf import settings

from pine.pine import Protocol
from pine.views.tests_support import PineTestCase, process_session

URL = '/threads'


class UnitThreadTestCase(PineTestCase):
    def setUp(self):
        self.client = Client()
        self.post_friend_thread_json = {
            'is_public': False,
            'content': 'Hello, Test content'
        }
        self.post_public_thread_json = {
            'is_public': True,
            'content': 'Hello, Test content'
        }
        self.get_friend_threads_json = {
            'is_friend': True,
            'offset': 0,
            'limit': 1
        }
        self.get_public_threads_json = {
            'is_friend': False,
            'offset': 0,
            'limit': 1
        }
        self.image_path = settings.BASE_DIR + '/resources/png_sample.png'

    def test_post_friends_thread_with_image(self):
        process_session(self.client, user_id=2)
        response = None
        with open(settings.BASE_DIR + '/resources/jpeg_sample.jpeg', 'rb') as fp:
            j = {
                'json': json.dumps(self.post_friend_thread_json),
                'bg_image_file': fp
            }
            response = self.client.post(URL, j).content.decode('utf-8')
            response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS, response

    def test_post_friends_thread_no_image(self):
        process_session(self.client, user_id=2)
        response = self.client.post(URL,
                                    data=json.dumps(self.post_friend_thread_json),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS, response

    def test_get_thread(self):
        process_session(self.client, user_id=2)
        response = self.client.get(URL+'/1', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert response[Protocol.DATA]['id'] == 1
        assert response[Protocol.DATA]['type'] == 0     # not author

        process_session(self.client, user_id=1)
        response = self.client.get(URL+'/1', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert response[Protocol.DATA]['type'] == 1     # author

    def test_post_thread_like(self):
        process_session(self.client, user_id=1)
        response = self.client.post(URL+'/8/like',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_post_thread_unlike(self):
        process_session(self.client, user_id=2)
        response = self.client.post(URL+'/2/unlike',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_post_report_thread(self):
        process_session(self.client, user_id=2)
        response = self.client.post(URL+'/7/report',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_post_report_thread_myself(self):
        process_session(self.client, user_id=1)
        response = self.client.post(URL+'/1/report',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.FAIL, response

    def test_block_thread(self):
        process_session(self.client, user_id=1)
        response = self.client.post(URL+'/5/block',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS, response[Protocol.MESSAGE]

    def test_block_thread_myself(self):
        process_session(self.client, user_id=1)
        response = self.client.post(URL+'/1/block',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.FAIL, response[Protocol.MESSAGE]


class IntegrationThreadTestCase(PineTestCase):
    def test_get_thread_after_report_thread(self):
        # report thread
        process_session(self.client, user_id=2)
        response = self.client.post(URL+'/1/block',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get thread
        response = self.client.get(URL+'/1', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.FAIL


class ReportedBugTestCase(PineTestCase):
    def test_like_unlike_like_crash(self):
        process_session(self.client, user_id=3)

        # like 8 thread
        response = self.client.post('/threads/8/like',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get like count
        response = self.client.get('/threads/8', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        before_like_count = response[Protocol.DATA]['like_count']

        # unlike thread
        response = self.client.post('/threads/8/unlike',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get like count
        response = self.client.get('/threads/8', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert response[Protocol.DATA]['like_count'] == before_like_count - 1

        # like thread
        response = self.client.post('/threads/8/like',
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
