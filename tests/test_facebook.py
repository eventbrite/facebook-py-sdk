import os
from unittest import TestCase

from facebook_sdk.authentication import AccessToken, OAuth2Client
from facebook_sdk.client import FacebookClient
from facebook_sdk.exceptions import FacebookSDKException
from facebook_sdk.facebook import FacebookApp, Facebook
from facebook_sdk.facebook_file import FacebookFile
from facebook_sdk.response import FacebookResponse
from tests import FakeFacebookClient, FakeResponse


class TestFacebook(TestCase):
    def setUp(self):
        super(TestFacebook, self).setUp()
        self.facebook = Facebook(
            app_id='123',
            app_secret='secret',
            default_access_token='my_token',
            default_graph_version='v2.6',
            default_request_timeout=10,
        )

    def test_initialize(self):
        self.assertIsInstance(self.facebook.app, FacebookApp)
        self.assertIsInstance(self.facebook.client, FacebookClient)
        self.assertIsInstance(self.facebook.oauth_client, OAuth2Client)

        self.assertEqual(self.facebook.app.app_id, '123')
        self.assertEqual(self.facebook.app.secret, 'secret')
        self.assertEqual(self.facebook.default_graph_version, 'v2.6')
        self.assertEqual(str(self.facebook.default_access_token), 'my_token')
        self.assertEqual(self.facebook.client.timeout, 10)

    def test_initialize_required_app_id_config(self):
        with self.assertRaises(FacebookSDKException):
            Facebook()

    def test_initialize_required_app_secret_config(self):
        with self.assertRaises(FacebookSDKException):
            Facebook(
                app_id='123',
            )

    def test_initialize_invalid_access_token(self):
        with self.assertRaises(ValueError):
            Facebook(
                app_id='123',
                app_secret='123',
                default_access_token=12345,
            )

    def test_send_request(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='',
                headers='',
            ),
        )
        response = self.facebook.send_request(
            method='GET',
            endpoint='some_endpoint',
            access_token='foo_token',
            graph_version='v2.7',
            timeout=182,
        )
        self.assertIsInstance(response, FacebookResponse)
        self.assertEqual(response.request.method, 'GET')
        self.assertEqual(response.request.endpoint, 'some_endpoint')
        self.assertEqual(response.request.access_token, 'foo_token')
        self.assertEqual(response.request.graph_version, 'v2.7')
        self.assertEqual(response.request.timeout, 182)
        self.assertDictEqual(response.request.params, {'access_token': 'foo_token'})

    def test_send_request_default_access_token_and_version(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='',
                headers='',
            )
        )
        response = self.facebook.send_request(
            method='GET',
            endpoint='some_endpoint',
        )

        self.assertEqual(response.request.method, 'GET')
        self.assertEqual(response.request.endpoint, 'some_endpoint')
        self.assertEqual(response.request.access_token, 'my_token')
        self.assertEqual(response.request.graph_version, 'v2.6')
        self.assertDictEqual(response.request.params, {'access_token': 'my_token'})

    def test_send_batch_request(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='[{"code":"200","body":"Foo"}]',
                headers='{"Content-Type": "application/json; charset=UTF-8","x-fb-trace-id": "1234"}'
            )
        )
        batches = [self.facebook.request(
            method='GET',
            endpoint='some_endpoint',
        )]

        response = self.facebook.send_batch_request(
            requests=batches,
            access_token='foo_token',
            graph_version='v2.7',
            timeout=182,
        )

        self.assertEqual(response.request.method, 'POST')
        self.assertEqual(response.request.access_token, 'foo_token')
        self.assertEqual(response.request.graph_version, 'v2.7')
        self.assertEqual(response.request.timeout, 182)
        self.assertDictEqual(response.request.params, {'access_token': 'foo_token'})

    def test_send_batch_request_default_access_token_and_version(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='[{"code":"200","body":"Foo"}]',
                headers='{"Content-Type": "application/json; charset=UTF-8","x-fb-trace-id": "1234"}'
            )
        )
        batches = [self.facebook.request(
            method='GET',
            endpoint='some_endpoint',
        )]

        response = self.facebook.send_batch_request(
            requests=batches,
        )

        self.assertEqual(response.request.method, 'POST')
        self.assertEqual(response.request.access_token, 'my_token')
        self.assertEqual(response.request.graph_version, 'v2.6')
        self.assertDictEqual(response.request.params, {'access_token': 'my_token'})

    def test_get_facebook_get_method(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='',
                headers='',
            )
        )
        response = self.facebook.get(
            endpoint='/test',
        )
        self.assertEqual(response.request.method, 'GET')

    def test_post_facebook_get_method(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='',
                headers='',
            )
        )
        response = self.facebook.post(
            endpoint='/test',
        )
        self.assertEqual(response.request.method, 'POST')

    def test_delete_facebook_get_method(self):
        self.facebook.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=200,
                content='',
                headers='',
            )
        )
        response = self.facebook.delete(
            endpoint='/test',
        )
        self.assertEqual(response.request.method, 'DELETE')

    def test_file_to_upload(self):
        facebook_file = self.facebook.file_to_upload(path='{base_path}/foo.txt'.format(
            base_path=os.path.dirname(os.path.abspath(__file__))
        ))

        self.assertIsInstance(facebook_file, FacebookFile)


class TestFacebookApp(TestCase):
    def setUp(self):
        super(TestFacebookApp, self).setUp()
        self.app = FacebookApp('id', 'secret')

    def test_initialize(self):
        self.assertEqual('id', self.app.app_id)
        self.assertEqual('secret', self.app.secret)

    def test_app_access_token_can_be_generated(self):
        self.assertTrue(isinstance(self.app.access_token(), AccessToken))
        self.assertEqual('id|secret', str(self.app.access_token()))
