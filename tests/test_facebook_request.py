# -*- coding: utf-8 -*-

import os
from unittest import TestCase

from facebook_sdk.constants import DEFAULT_GRAPH_VERSION, METHOD_POST, METHOD_GET, METHOD_DELETE
from facebook_sdk.exceptions import FacebookSDKException
from facebook_sdk.facebook_file import FacebookFile
from facebook_sdk.request import FacebookBatchRequest, FacebookRequest
from facebook_sdk.utils import force_slash_prefix


class TestFacebookRequest(TestCase):
    def test_get_request_has_access_token(self):
        access_token = 'fake_token'
        request = FacebookRequest(
            endpoint='',
            access_token=access_token,
            method=METHOD_GET,
        )
        self.assertTrue('access_token' in request.params)
        self.assertEqual(request.params.get('access_token'), access_token)

    def test_post_request_has_access_token(self):
        access_token = 'fake_token'
        request = FacebookRequest(
            endpoint='',
            access_token=access_token,
            method=METHOD_POST,
        )
        self.assertTrue('access_token' in request.params)
        self.assertEqual(request.params.get('access_token'), access_token)

    def test_post_params(self):
        expected_post_params = {'foo': 'bar'}
        request = FacebookRequest(
            endpoint='',
            method=METHOD_POST,
            params=expected_post_params
        )
        self.assertFalse(request.params)
        self.assertDictEqual(request.post_params, expected_post_params)

    def test_encoded_body(self):
        request = FacebookRequest(
            endpoint='',
            method=METHOD_POST,
            params={'foo': 'bar'}
        )
        self.assertFalse(request.params)
        self.assertEqual(request.url_encode_body, 'foo=bar')

    def test_default_attributes(self):
        request = FacebookRequest(endpoint='')
        self.assertIsInstance(request.headers, dict)
        self.assertIsInstance(request.params, dict)
        self.assertEqual(request.graph_version, DEFAULT_GRAPH_VERSION)

    def test_endpoint_url(self):
        request = FacebookRequest(endpoint='/foo')
        self.assertEqual(request.url, force_slash_prefix(DEFAULT_GRAPH_VERSION) + '/foo')

    def test_endpoint_with_access_token(self):
        request = FacebookRequest(endpoint='/foo?access_token=foo_token')
        self.assertEqual(request.url, force_slash_prefix(DEFAULT_GRAPH_VERSION) + '/foo')
        self.assertEqual(request.access_token, 'foo_token')

    def test_endpoint_with_distinct_access_tokens(self):
        with self.assertRaises(FacebookSDKException):
            FacebookRequest(
                endpoint='/foo?access_token=foo_token',
                access_token='bar_token',
            )

    def test_empty_endpoint_url(self):
        request = FacebookRequest(endpoint='')
        self.assertEqual(request.url, force_slash_prefix(DEFAULT_GRAPH_VERSION) + '/')

    def test_extract_files_from_params(self):
        request = FacebookRequest(
            endpoint='',
            params={
                'message': 'Awesome Photo',
                'source': FacebookFile(
                    path='{base_path}/foo.txt'.format(
                        base_path=os.path.dirname(os.path.abspath(__file__))
                    ),
                )
            }
        )

        self.assertFalse('source' in request._params)
        self.assertIn('source', request.files)

    def test_contains_file(self):
        request_with_file = FacebookRequest(
            endpoint='',
            params={
                'message': 'Awesome Photo',
                'source': FacebookFile(
                    path='{base_path}/foo.txt'.format(
                        base_path=os.path.dirname(os.path.abspath(__file__))
                    ),
                )
            }
        )
        request = FacebookRequest(endpoint='')

        self.assertTrue(request_with_file.contain_files())
        self.assertFalse(request.contain_files())

    def test_files_to_upload(self):
        facebook_file = FacebookFile(
            path='{base_path}/foo.txt'.format(
                base_path=os.path.dirname(os.path.abspath(__file__))
            ),
        )
        request = FacebookRequest(
            endpoint='',
            params={
                'message': 'Awesome Photo',
                'source': facebook_file
            }
        )
        files_to_upload = request.files_to_upload()[0]
        expected = ('source', ('foo.txt', facebook_file, 'text/plain'))
        self.assertEqual(files_to_upload, expected)


class TestFacebookBatchRequest(TestCase):

    def setUp(self):
        self.req1 = FacebookRequest(
            endpoint='123',
            method=METHOD_GET,
            headers={'Conent-Type': 'application/json'},
        )
        self.req2 = FacebookRequest(
            endpoint='123',
            method=METHOD_POST,
            params={'foo': u'bár'},
        )
        self.req3 = FacebookRequest(
            access_token='other_token',
            endpoint='123',
            method=METHOD_DELETE,
        )
        self.req4 = FacebookRequest(
            endpoint='123',
            method=METHOD_GET,
            params={'fields': u'name, descriptión'},
            headers={'Conent-Type': 'application/json'},
        )

    def test_add_a_list_of_requests(self):
        requests = [self.req1, self.req2]
        batch_request = FacebookBatchRequest(
            requests=[self.req1, self.req2],
            access_token='fake_token'
        )

        for request in batch_request.requests:
            self.assertTrue(request['request'] in requests)

    def test_add_a_named_dict_of_requests(self):
        requests = {
            'first': self.req1,
            'second': self.req2,
            'third': self.req3,
        }
        batch_request = FacebookBatchRequest(
            requests=requests,
            access_token='fake_token'
        )
        batch_request.prepare_batch_request()

        for request in batch_request:
            self.assertEqual(requests[request['name']], request['request'])

    def test_prepare_batch_request(self):
        batch_request = FacebookBatchRequest(
            access_token='fake_token',
            requests=[self.req1, self.req2, self.req3]
        )
        expected_batch = (
            '[{"headers": {"Conent-Type": "application/json"}, "method": "GET", "relative_url": "/v2.12/123?access_token=fake_token", "name": "0"}, '
            '{"body": "foo=b%C3%A1r", "headers": {}, "method": "POST", "relative_url": "/v2.12/123", "name": "1"}, '
            '{"access_token": "other_token", "headers": {}, "method": "DELETE", "relative_url": "/v2.12/123?access_token=other_token", "name": "2"}]'
        )
        batch_request.prepare_batch_request()
        self.assertEqual(sorted(batch_request.post_params['batch']), sorted(expected_batch))
        self.assertTrue(batch_request.post_params['include_headers'])

    def test_prepare_batch_request_with_params(self):
        batch_request = FacebookBatchRequest(
            access_token='fake_token',
            requests=[self.req1, self.req4]
        )
        expected_batch = (
            '[{"headers": {"Conent-Type": "application/json"}, "method": "GET", "relative_url": "/v2.12/123?access_token=fake_token", "name": "0"}, '
            '{"headers": {"Conent-Type": "application/json"}, "method": "GET", "relative_url": "/v2.12/123?access_token=fake_token&fields=name%2C+descripti%C3%B3n", "name": "1"}]'
        )

        batch_request.prepare_batch_request()
        self.assertEqual(sorted(batch_request.post_params['batch']), sorted(expected_batch))
        self.assertTrue(batch_request.post_params['include_headers'])


    def test_request_entity_to_batch_array(self):
        pass

    def test_requests_to_json_str(self):
        pass

    def test_batch_request_with_files(self):
        request = FacebookRequest(
            endpoint='/foo',
            method='POST',
            params={
                'message': 'foo',
                'source': FacebookFile(
                    path='{base_path}/foo.txt'.format(
                        base_path=os.path.dirname(os.path.abspath(__file__))
                    ),
                )
            }
        )
        batch_request = FacebookBatchRequest(
            access_token='fake_token',
            requests=[request],
        )
        expected_batch = '[{"body": "message=foo", "attached_files": "%(attached_files)s", "name": "0", "relative_url": "/v2.12/foo", "headers": {}, "method": "POST"}]' % dict(attached_files=batch_request.requests[0].get('attached_files'))
        batch_request.prepare_batch_request()

        self.assertEqual(sorted(batch_request.post_params['batch']), sorted(expected_batch))
