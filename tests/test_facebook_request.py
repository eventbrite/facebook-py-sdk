from unittest import TestCase

from facebook_sdk.request import FacebookBatchRequest


class TestFacebookRequest(TestCase):
    def test_params(self):
        self.fail()

    def test_post_params(self):
        self.fail()

    def test_url(self):
        self.fail()

    def test_url_encode_body(self):
        self.fail()

    def test_add_headers(self):
        self.fail()


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
