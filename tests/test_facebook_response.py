import json

from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.request import FacebookRequest
from facebook_sdk.response import FacebookResponse, FacebookBatchResponse
from tests import FakeFacebookRequest, FakeFacebookBatchRequest, TestCase


class TestFacebookResponse(TestCase):
    def test_parse_body(self):
        expected_body = {'success': True}
        response = FacebookResponse(
            request=FakeFacebookRequest,
            body=json.dumps(expected_body),
            http_status_code=200
        )
        self.assertEqual(expected_body, response.json_body)

    def test_raise_exception(self):
        response = FacebookResponse(
            request=FakeFacebookRequest,
            body=json.dumps({'error': {'foo': 'bar'}}),
            http_status_code=200
        )

        self.assertRaises(
            FacebookResponseException,
            response.raiseException,
        )

    def test_build_exception(self):
        response = FacebookResponse(
            request=FakeFacebookRequest,
            body=json.dumps({'error': {'foo': 'bar'}}),
            http_status_code=200
        )
        self.assertIsInstance(response.exception, FacebookResponseException)


class TestFacebookBatchResponse(TestCase):
    def setUp(self):
        super(TestFacebookBatchResponse, self).setUp()

        self.req1 = FacebookRequest(endpoint='123', method='get')
        self.req2 = FacebookRequest(endpoint='123', method='post', params={'foo': 'bar'})
        self.batch_request = FakeFacebookBatchRequest(requests=[self.req1, self.req2])
        self.response = FacebookResponse(
            request=self.batch_request,
            body=json.dumps([
                {
                    'headers': {},
                    'code': 200,
                    'body': {'foo': 'bar'}
                },
                {
                    'headers': {},
                    'code': 200,
                    'body': {'success': True}
                },
            ]),
            http_status_code=200
        )

    def test_build_responses(self):
        batch_response = FacebookBatchResponse(
            batch_request=self.batch_request,
            batch_response=self.response,
        )

        self.assertEqual(len(batch_response.responses), 2)

        for index, response_dict in enumerate(batch_response.responses):
            request_dict = self.batch_request.requests[index]
            self.assertEqual(response_dict.get('name'), request_dict.get('name'))
            self.assertEqual(response_dict.get('response').request, request_dict.get('request'))
