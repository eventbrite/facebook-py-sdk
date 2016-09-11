from facebook_sdk.client import FacebookClient
from facebook_sdk.constants import BASE_GRAPH_URL
from facebook_sdk.exceptions import FacebookResponseException, FacebookSDKException
from facebook_sdk.request import FacebookRequest, FacebookBatchRequest
from facebook_sdk.response import FacebookResponse, FacebookBatchResponse
from tests import TestCase


class FakeFacebookClient(FacebookClient):
    def __init__(self, fake_response):
        super(FakeFacebookClient, self).__init__()
        self.fake_response = fake_response

    def send(self, *args, **kwargs):
        return self.fake_response


class FakeResponse():
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code


class TestFacebookClient(TestCase):
    def setUp(self):
        super(TestFacebookClient, self).setUp()
        self.request = FacebookRequest(endpoint='')
        self.batch_request = FacebookBatchRequest(
            access_token='fake_token',
            requests=[self.request]
        )
        self.fake_response = FakeResponse(
            status_code=200,
            content='{"data":[{"id":"123","name":"Foo"},{"id":"1337","name":"Bar"}]}'
        )
        self.fake_batch_response = FakeResponse(
            status_code=200,
            content='[{"code":"123","body":"Foo"}]'
        )

        self.client = FakeFacebookClient(fake_response=self.fake_response)

    def test_prepare_request(self):
        (method, url, params, data, headers) = self.client._prepareRequest(request=self.request)

        self.assertEqual(method, self.request.method)
        self.assertEqual(url, '{}/{}'.format(BASE_GRAPH_URL, self.request.url))
        self.assertEqual(params, self.request.params)
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Content-Type'], 'application/x-www-form-urlencoded')

    def test_send_request(self):
        response = self.client.send_request(self.request)
        self.assertIsInstance(response, FacebookResponse)

    def test_send_request_error(self):
        self.client = FakeFacebookClient(
            fake_response=FakeResponse(
                status_code=400,
                content='{"error": {"code": 100}}')
        )
        with self.assertRaises(FacebookResponseException) as context:
            self.client.send_request(self.request)

    def test_send_batch_request(self):
        self.client = FakeFacebookClient(
            fake_response=self.fake_batch_response
        )
        response = self.client.send_batch_request(
            batch_request=self.batch_request
        )
        self.assertIsInstance(response, FacebookBatchResponse)

    def test_send_empty_batch_request(self):
        with self.assertRaises(FacebookSDKException) as context:
            self.client.send_batch_request(
                batch_request=FacebookBatchRequest(
                    access_token='fake_token'
                )
            )

    def test_send_over_limit_batch_request(self):
        with self.assertRaises(FacebookSDKException) as context:
            requests = [self.request] * 51
            self.client.send_batch_request(
                batch_request=FacebookBatchRequest(
                    access_token='fake_token',
                    requests=requests
                )
            )