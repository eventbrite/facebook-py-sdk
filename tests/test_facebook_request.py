from facebook_sdk.constants import DEFAULT_GRAPH_VERSION
from facebook_sdk.request import FacebookBatchRequest, FacebookRequest
from tests import TestCase


class TestFacebookRequest(TestCase):
    def setUp(self):
        super(TestFacebookRequest, self).setUp()

    def test_get_request_has_access_token(self):
        access_token = 'fake_token'
        request = FacebookRequest(
            access_token=access_token,
            method='get',
        )
        self.assertTrue('access_token' in request.params)
        self.assertEqual(request.params.get('access_token'), access_token)

    def test_post_request_has_access_token(self):
        access_token = 'fake_token'
        request = FacebookRequest(
            access_token=access_token,
            method='post',
        )
        self.assertTrue('access_token' in request.params)
        self.assertEqual(request.params.get('access_token'), access_token)

    def test_post_params(self):
        expected_post_params = {'foo': 'bar'}
        request = FacebookRequest(
            method='post',
            params=expected_post_params
        )
        self.assertFalse(request.params)
        self.assertDictEqual(request.post_params, expected_post_params)

    def test_encoded_body(self):
        request = FacebookRequest(
            method='post',
            params={'foo': 'bar'}
        )
        self.assertFalse(request.params)
        self.assertEqual(request.url_encode_body, 'foo=bar')

    def test_default_attributes(self):
        request = FacebookRequest()
        self.assertIsInstance(request.headers, dict)
        self.assertIsInstance(request.params, dict)
        self.assertEqual(request.graph_version, DEFAULT_GRAPH_VERSION)

    def test_endpoint_url(self):
        request = FacebookRequest(endpoint='foo')
        self.assertEqual(request.url, DEFAULT_GRAPH_VERSION + '/foo/')

    def test_empty_endpoint_url(self):
        request = FacebookRequest(endpoint='')
        self.assertEqual(request.url, DEFAULT_GRAPH_VERSION + '/')


class TestFacebookBatchRequest(TestCase):
    def setUp(self):
        super(TestFacebookBatchRequest, self).setUp()
        self.req1 = FacebookRequest(
            endpoint='123',
            method='get',
            headers={'Conent-Type': 'application/json'}
        )
        self.req2 = FacebookRequest(
            endpoint='123',
            method='post',
            params={'foo': 'bar'}
        )
        self.req3 = FacebookRequest(
            access_token='other_token',
            endpoint='123',
            method='delete'
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
            '[{"headers": {"Conent-Type": "application/json"}, "method": "get", "relative_url": "v2.5/123/", "name": "0"}, '
            '{"body": "foo=bar", "headers": {}, "method": "post", "relative_url": "v2.5/123/", "name": "1"}, '
            '{"access_token": "other_token", "headers": {}, "method": "delete", "relative_url": "v2.5/123/", "name": "2"}]'
        )
        batch_request.prepare_batch_request()
        self.assertEqual(sorted(batch_request.post_params['batch']), sorted(expected_batch))
        self.assertTrue(batch_request.post_params['include_headers'])

    def test_request_entity_to_batch_array(self):
        pass

    def test_requests_to_json(self):
        pass
