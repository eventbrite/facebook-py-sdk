import json
from unittest import TestCase

from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.response import FacebookResponse
from tests import FakeFacebookRequest


class TestFacebookResponse(TestCase):

    def test_parse_body(self):
        expected_body = {'success': True}
        response = FacebookResponse(
            request=FakeFacebookRequest,
            body=json.dumps(expected_body),
            http_status_code=200
        )
        self.assertEqual(expected_body, response.json_body )

    def test_raiseException(self):
        response = FacebookResponse(
            request=FakeFacebookRequest,
            body=json.dumps({'error': {'foo': 'bar'}}),
            http_status_code=200
        )

        with self.assertRaises(FacebookResponseException) as context:
            response.raiseException()

    def test_build_exception(self):
        response = FacebookResponse(
            request=FakeFacebookRequest,
            body=json.dumps({'error': {'foo': 'bar'}}),
            http_status_code=200
        )
        self.assertIsInstance(response.exception, FacebookResponseException)
