from unittest import TestCase

from facebook_sdk.constants import DEFAULT_GRAPH_VERSION
from facebook_sdk.request import FacebookBatchRequest, FacebookRequest


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
        expected_post_params = {'foo':'bar'}
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
        self.batch_request = FacebookBatchRequest()

    def test_add(self):
        self.fail()

    def test_add_access_token(self):
        self.fail()

    def test_prepare_batch_request(self):
        self.fail()

    def test_request_entity_to_batch_array(self):
        self.fail()

    def test_requests_to_json(self):
        self.fail()
