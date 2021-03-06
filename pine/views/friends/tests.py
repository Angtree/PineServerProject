import json

from django.test import TestCase
from django.test.client import Client

from pine.pine import Protocol
from pine.views.tests_support import PineTestCase, process_session


class UnitThreadTestCase(PineTestCase):
    def setUp(self):
        self.post_friends_create_no_pine_user = {
            'phone_numbers': ['01088888878', '01088888788']
        }
        self.post_friends_create_pine_user = {
            'phone_numbers': ['01032080403']
        }
        self.post_friends_create_pine_user2 = {
            'phone_numbers': ['01020863441']
        }
        self.post_friends_destroy_pine_user = {
            'phone_numbers': ['01098590530']
        }
        self.post_friends_destroy_pine_user2 = {
            'phone_numbers': ['01040099179', '01087537711', '01098590530']
        }

    def test_get_friends_list(self):
        process_session(self.client, user_id=2)
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_create_no_pine_friend_to_user(self):
        process_session(self.client, user_id=2)
        response = self.client.post('/friends/create',
                                    data=json.dumps(self.post_friends_create_no_pine_user),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_create_pine_friend_to_user_becoming_each_other_friends(self):
        process_session(self.client, user_id=9)
        response = self.client.post('/friends/create',
                                    data=json.dumps(self.post_friends_create_pine_user),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_create_pine_friend_to_user_becoming_user_following(self):
        process_session(self.client, user_id=2)
        response = self.client.post('/friends/create',
                                    data=json.dumps(self.post_friends_create_pine_user2),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_destroy_pine_friend_each_other_friends(self):
        process_session(self.client, user_id=1)
        response = self.client.post('/friends/destroy',
                                    data=json.dumps(self.post_friends_destroy_pine_user),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_destroy_pine_friend_user_following(self):
        process_session(self.client, user_id=2)
        response = self.client.post('/friends/destroy',
                                    data=json.dumps(self.post_friends_destroy_pine_user2),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_get_handshake_friends_count(self):
        process_session(self.client, user_id=1)
        response = self.client.get('/friends/handshake_count', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_get_friends_who_are_user(self):
        process_session(self.client, user_id=1)
        response = self.client.post('/friends/get',
                                    data=json.dumps(self.post_friends_destroy_pine_user2),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS


class IntegrationTestCase(PineTestCase):
    def test_destroy_friend_after_add_no_pine_friend(self):
        # create friendship with no pine user
        process_session(self.client, user_id=3)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ["01087877711", "01099991111", "01087871111", "01098514123"]
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get friends list count
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        before_friends_count = len(response[Protocol.DATA])

        # destroy friendship
        response = self.client.post('/friends/destroy',
                                    data=json.dumps({
                                        'phone_numbers': ["01087877711", "01099991111", "01087871111", "01098514123"]
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get friends list count after destroy friendship
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert before_friends_count == len(response[Protocol.DATA]) + 4


class ReportedBugTestCase(PineTestCase):
    def user_3_add_x2_friendship_is_crashed(self):
        process_session(self.client, user_id=3)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ['01087877711', '01099991111', '01087871111']
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ['01087877711', '01099991111', '01087871111']
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_destroy_all_friend_after_add_no_pine_friend_and_pine_friend_x2(self):
        # create friendship with pine, no pine user
        process_session(self.client, user_id=3)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ["01032080403", "01099991111"]
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # create friendship with no pine user again
        process_session(self.client, user_id=3)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ["01087537711"]
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get friends list count
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        before_friends_count = len(response[Protocol.DATA])

        # destroy friendship
        response = self.client.post('/friends/destroy',
                                    data=json.dumps({
                                        'phone_numbers': ["01032080403", "01099991111", '01087537711']
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get friends list count after destroy friendship
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert before_friends_count == len(response[Protocol.DATA]) + 3

        # create friendship with pine, no pine user
        process_session(self.client, user_id=3)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ["01032080403", "01099991111"]
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get friends list count
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        before_friends_count = len(response[Protocol.DATA])

        # destroy friendship
        response = self.client.post('/friends/destroy',
                                    data=json.dumps({
                                        'phone_numbers': ["01032080403", "01099991111"]
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        # get friends list count after destroy friendship
        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert before_friends_count == len(response[Protocol.DATA]) + 2

    def test_create_duplicated_friendship(self):
        process_session(self.client, user_id=3)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ['01011111111', '01011111111']
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ['01011111111', '01011111111']
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

    def test_create_friendship_herself(self):
        process_session(self.client, user_id=1)
        response = self.client.post('/friends/create',
                                    data=json.dumps({
                                        'phone_numbers': ['01032080403']
                                    }),
                                    content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS

        response = self.client.get('/friends/list', content_type='application/json').content.decode('utf-8')
        response = json.loads(response)
        assert response[Protocol.RESULT] == Protocol.SUCCESS
        assert not '01032080403' in response[Protocol.DATA]
