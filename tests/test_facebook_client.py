# coding=utf-8
import os
from unittest import TestCase

from facebook_sdk.constants import BASE_GRAPH_URL
from facebook_sdk.exceptions import FacebookResponseException, FacebookSDKException
from facebook_sdk.facebook_file import FacebookFile
from facebook_sdk.request import FacebookBatchRequest, FacebookRequest
from facebook_sdk.response import FacebookBatchResponse, FacebookResponse
from tests import FakeFacebookClient, FakeResponse


class TestFacebookClient(TestCase):
    def setUp(self):
        super(TestFacebookClient, self).setUp()
        self.request = FacebookRequest(endpoint='me', method='GET')
        self.batch_request = FacebookBatchRequest(
            access_token='fake_token',
            requests=[self.request]
        )
        self.fake_response = FakeResponse(
            status_code=200,
            content='{"data":[{"id":"123","name":"Foo"},{"id":"1337","name":"Bar"}]}',
            headers='{"Content-Type": "application/json; charset=UTF-8","x-fb-trace-id": "1234"}',
        )
        self.fake_batch_response = FakeResponse(
            status_code=200,
            content='[{"code":"123","body":"Foo"}]',
            headers='{"Content-Type": "application/json; charset=UTF-8","x-fb-trace-id": "1234"}',
        )

        self.client = FakeFacebookClient(fake_response=self.fake_response)

    def test_prepare_request(self):
        request_params = self.client._prepareRequest(request=self.request)

        self.assertEqual(request_params.get('method'), self.request.method)
        self.assertEqual(request_params.get('url'), '%s%s' % (BASE_GRAPH_URL, self.request.url))
        self.assertEqual(request_params.get('params'), self.request.params)
        self.assertIn('Content-Type', request_params.get('headers'))
        self.assertEqual(request_params.get('headers').get('Content-Type'), 'application/x-www-form-urlencoded')

    def test_prepare_request_with_ascii_encoded_params(self):
        request = FacebookRequest(
            endpoint='events',
            method='POST',
            params={
                'foo': u'ánother boRken param',
            },
        )
        request_params = self.client._prepareRequest(request=request)
        self.assertEqual(request_params.get('method'), request.method)

    def test_send_request(self):
        response = self.client.send_request(self.request)

        self.assertIsInstance(response, FacebookResponse)
        self.assertDictContainsSubset({
            'method': 'GET',
            'url': 'https://graph.facebook.com/v2.12/me',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'params': {'access_token': 'fake_token'},
            'files': [],
            'timeout': 60,
            'data': None,
        }, self.client.send_kwargs)

    def test_send_request_override_timeout(self):
        self.client = FakeFacebookClient(
            fake_response=self.fake_response,
            request_timeout=10,
        )
        self.client.send_request(self.request)

        self.assertDictEqual({
            'method': 'GET',
            'url': 'https://graph.facebook.com/v2.12/me',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'params': {'access_token': 'fake_token'},
            'files': [],
            'timeout': 10,
            'data': None,
        }, self.client.send_kwargs)

    def test_send_request_with_file(self):
        file_to_upload = FacebookFile(
            path='{base_path}/foo.txt'.format(
                base_path=os.path.dirname(os.path.abspath(__file__))
            ),
        )
        request = FacebookRequest(
            endpoint='photos',
            method='POST',
            params={
                'message': 'Awesome Photo',
                'source': file_to_upload,
            },
            access_token='fake_token',
        )
        self.client = FakeFacebookClient(
            fake_response=self.fake_response,
        )
        self.client.send_request(request)
        self.assertDictEqual({
            'method': 'POST',
            'url': 'https://graph.facebook.com/v2.12/photos',
            'headers': {},
            'params': {'access_token': 'fake_token'},
            'files': [('source', ('foo.txt', file_to_upload, 'text/plain'))],
            'timeout': 60,
            'data': {'message': 'Awesome Photo'},
        }, self.client.send_kwargs)

    def test_send_request_error(self):
        self.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=400,
                content='{"error": {"code": 100}}',
                headers='{"Content-Type": "application/json; charset=UTF-8","x-fb-trace-id": "1234"}',
            )
        )
        with self.assertRaises(FacebookResponseException):
            self.client.send_request(self.request)

    def test_send_batch_request(self):
        self.client = FakeFacebookClient(
            fake_response=self.fake_batch_response,
        )
        response = self.client.send_batch_request(
            batch_request=self.batch_request,
        )
        self.assertIsInstance(response, FacebookBatchResponse)
        self.assertDictContainsSubset({
            'method': 'POST',
            'url': 'https://graph.facebook.com/v2.12/',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'params': {'access_token': 'fake_token'},
            'files': [],
            'timeout': 60,
        }, self.client.send_kwargs)

    def test_send_empty_batch_request(self):
        with self.assertRaises(FacebookSDKException):
            self.client.send_batch_request(
                batch_request=FacebookBatchRequest(
                    access_token='fake_token',
                ),
            )

    def test_send_over_limit_batch_request(self):
        requests = [self.request] * 51
        with self.assertRaises(FacebookSDKException):
            self.client.send_batch_request(
                batch_request=FacebookBatchRequest(
                    access_token='fake_token',
                    requests=requests,
                ),
            )
