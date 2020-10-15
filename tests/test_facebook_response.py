import json
from unittest import TestCase

from facebook_sdk.constants import METHOD_GET, METHOD_POST
from facebook_sdk.exceptions import FacebookResponseException, FacebookSDKException
from facebook_sdk.request import FacebookRequest
from facebook_sdk.response import FacebookResponse, FacebookBatchResponse
from tests import FakeFacebookRequest, FakeFacebookBatchRequest


class TestFacebookResponse(TestCase):
    def test_parse_body(self):
        expected_body = {'success': True}
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=json.dumps(expected_body),
            http_status_code=200
        )
        self.assertEqual(expected_body, response.json_body)

    def test_parse_body_for_bytestrings(self):
        expected_body = {'success': True}
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=b'{"success": true}',
            http_status_code=200,
        )
        self.assertEqual(expected_body, response.json_body)

    def test_check_for_headers(self):
        expected_body = {'success': True}
        expected_headers = {'x-fb-trace-id': '1234'}
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=json.dumps(expected_body),
            headers=expected_headers,
            http_status_code=200
        )
        self.assertEqual(expected_headers, response.headers)

    def test_raise_exception(self):
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=json.dumps({'error': {'foo': 'bar'}}),
            http_status_code=200
        )

        with self.assertRaises(FacebookResponseException):
            response.raiseException()

    def test_build_exception(self):
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=json.dumps({'error': {'foo': 'bar'}}),
            http_status_code=200
        )
        self.assertIsInstance(response.exception, FacebookResponseException)


class TestFacebookResponsePagination(TestCase):
    def setUp(self):
        super(TestFacebookResponsePagination, self).setUp()
        self.paginable_body = {
            'data': [{
                'images': [
                    {
                        'height': 960,
                        'source': 'https://fbcdn-sphotos-a-a.akamaihd.net/hphotos-ak-xtf1/t31.0-8/1290121r2_1173774305979756_75759041928559429558_o.jpg',
                        'width': 1280
                    },
                    {
                        'height': 720,
                        'source': 'https://fbcdn-sphotos-a-a.akamaihd.net/hphotos-ak-xfp1/v/t1.0-9/12495117_1173774305979756_4579041928559429558_n.jpg?oh=f4066e6b8bb9c6db1aea2e07d30f6bd8&oe=588D2B3D&__gda__=1485370477_c221b76e4a897ced0894126abc1553f5',
                        'width': 960
                    },
                    {
                        'height': 600,
                        'source': 'https://fbcdn-photos-a-a.akamaihd.net/hphotos-ak-xtf1/t31.0-0/p600x600/12901212_1173774305979756_75790419428559429558_o.jpg',
                        'width': 800
                    },
                ]
            }],
            'paging': {
                'cursors': {
                    'before': 'TVRFM016YzNORE13TlRrM09UYzFOam94TkRVNU5EUTRNVGczT2pNNU5EQTRPVFkwTURZAME56ZA3pOZAz09',
                    'after': 'TVRBeU1EWTNOVFUyTmpVeE1Ea3hOREU2TVRRek16Y3dPREl4TVRvek9UUXdPRGsyTkRBMk5EYzRNelk9'
                },
                'next': 'https://graph.facebook.com/v2.7/me/photos?access_token=foo_token&pretty=0&fields=images&limit=25&after=TVRBeU1EWTNOVFUyTmpVeE1Ea3hOREU2TVRRek16Y3dPREl4TVRvek9UUXdPRGsyTkRBMk5EYzRNelk9',
                'previous': 'https://graph.facebook.com/v2.7/me/photos?access_token=foo_token&pretty=0&fields=images&limit=25&before=TVRFM016YzNORE13TlRrM09UYzFOam94TkRVNU5EUTRNVGczT2pNNU5EQTRPVFkwTURZAME56ZA3pOZAz09',
            }
        }
        self.response = FacebookResponse(
            request=FacebookRequest(
                endpoint='/me/photos',
                method='GET',
                params={'foo': 'bar'},
                access_token='foo_token',
            ),
            body=json.dumps(self.paginable_body),
            http_status_code=200
        )

    def test_next_page(self):
        request = self.response.next_page_request()

        self.assertEqual(sorted(request.endpoint), sorted('/me/photos?pretty=0&fields=images&limit=25&after=TVRBeU1EWTNOVFUyTmpVeE1Ea3hOREU2TVRRek16Y3dPREl4TVRvek9UUXdPRGsyTkRBMk5EYzRNelk9'))
        self.assertNotEqual(self.response.request, request)

    def test_previous_page(self):
        request = self.response.previous_page_request()

        self.assertEqual(sorted(request.endpoint), sorted('/me/photos?pretty=0&fields=images&limit=25&before=TVRFM016YzNORE13TlRrM09UYzFOam94TkRVNU5EUTRNVGczT2pNNU5EQTRPVFkwTURZAME56ZA3pOZAz09'))
        self.assertNotEqual(self.response.request, request)

    def test_http_allowed_method_for_pagination(self):
        self.response.request.method = 'POST'

        with self.assertRaises(FacebookSDKException):
            self.response.next_page_request()


class TestFacebookBatchResponse(TestCase):
    def setUp(self):
        super(TestFacebookBatchResponse, self).setUp()

        self.req1 = FacebookRequest(endpoint='123', method=METHOD_GET)
        self.req2 = FacebookRequest(endpoint='123', method=METHOD_POST, params={'foo': 'bar'})
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

        for index, response_dict in enumerate(batch_response):
            request_dict = self.batch_request.requests[index]
            self.assertEqual(response_dict.get('name'), request_dict.get('name'))
            self.assertEqual(response_dict.get('response').request, request_dict.get('request'))


class TestFacebookResponseException(TestCase):

    def test_raise_exception_from_complete_error(self):
        """Test a failed response triggers a correctly populated exception.

        Consider all the error fields specified in:
        https://developers.facebook.com/docs/graph-api/using-graph-api/error-handling
        """
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=json.dumps({
                'error': {
                    'message': 'Message describing the error',
                    'type': 'OAuthException',
                    'code': 190,
                    'error_subcode': 460,
                    'error_user_title': 'A title',
                    'error_user_msg': 'A message',
                    'fbtrace_id': 'EJplcsCHuLu',
                },
            }),
            http_status_code=200
        )

        with self.assertRaises(FacebookResponseException) as cm:
            response.raiseException()
        exception = cm.exception

        self.assertEqual(exception.code, 190)
        self.assertEqual(exception.error_subcode, 460)
        self.assertEqual(exception.error_user_title, 'A title')
        self.assertEqual(exception.error_user_msg, 'A message')
        self.assertEqual(exception.message, 'Message describing the error')
        self.assertEqual(exception.type, 'OAuthException')

    def test_raise_exception_from_incomplete_error(self):
        """Test a failed response without all the information triggers a correctly populated exception."""
        response = FacebookResponse(
            request=FakeFacebookRequest(),
            body=json.dumps({
                'error': {
                    'message': 'Message describing the error',
                    'type': 'OAuthException',
                    'code': 190,
                    'error_subcode': 460,
                    'fbtrace_id': 'EJplcsCHuLu',
                },
            }),
            http_status_code=200
        )

        with self.assertRaises(FacebookResponseException) as cm:
            response.raiseException()
        exception = cm.exception

        self.assertEqual(exception.code, 190)
        self.assertEqual(exception.error_subcode, 460)
        self.assertEqual(exception.error_user_title, '')
        self.assertEqual(exception.error_user_msg, '')
        self.assertEqual(exception.message, 'Message describing the error')
        self.assertEqual(exception.type, 'OAuthException')
