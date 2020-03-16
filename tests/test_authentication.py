import datetime
from unittest import TestCase

from facebook_sdk import __version__ as VERSION
from facebook_sdk.authentication import AccessToken, OAuth2Client
from facebook_sdk.facebook import FacebookApp
from tests import FakeOAuth2Client

from six.moves.urllib.parse import quote_plus


class TestAccessToken(TestCase):
    def setUp(self):
        super(TestAccessToken, self).setUp()
        self.foo_token = 'foo_token'
        self.app_token = 'app|secret'

    def test_initialize(self):
        access_token = AccessToken(self.foo_token)

        self.assertEqual(access_token.access_token, self.foo_token)

    def test_is_valid_access_token(self):
        access_token = AccessToken(self.foo_token)
        app_access_token = AccessToken(self.app_token)

        self.assertFalse(access_token.is_app_access_token())
        self.assertTrue(app_access_token.is_app_access_token())

    def test_app_secret_proof(self):
        access_token = AccessToken(self.foo_token)
        app_secret_proof = access_token.app_secret_proof('shhhhh!is.my.secret')

        self.assertEqual('796ba0d8a6b339e476a7b166a9e8ac0a395f7de736dc37de5f2f4397f5854eb8', app_secret_proof)

    def test_short_lived_access_token(self):
        an_hour_from_now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        access_token = AccessToken(self.foo_token, expires_at=an_hour_from_now)

        self.assertFalse(access_token.is_long_lived())

    def test_long_lived_access_token(self):
        a_week_from_now = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        access_token = AccessToken(self.foo_token, expires_at=a_week_from_now)

        self.assertTrue(access_token.is_long_lived())

    def test_access_token_do_not_expires(self):
        app_access_token = AccessToken(self.app_token)

        self.assertFalse(app_access_token.is_expired())

    def test_access_token_expires(self):
        an_minute_before_from_now = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        access_token = AccessToken(self.foo_token, expires_at=an_minute_before_from_now)

        self.assertTrue(access_token.is_expired())


class OAuth2ClientTest(TestCase):
    def setUp(self):
        super(OAuth2ClientTest, self).setUp()
        self.app = FacebookApp(
            app_id='app_id',
            app_secret='secret'
        )

    def test_debug_token(self):
        fb_client = FakeOAuth2Client(
            http_status_code=200,
            body='{"data":{"user_id":"444"}}',
            headers=[]
        )
        oauth_client = OAuth2Client(app=self.app, client=fb_client, graph_version='v2.12')
        metadata = oauth_client.debug_token(access_token='foo_token')

        self.assertEqual(metadata.get('data').get('user_id'), '444')

        request = oauth_client.last_request
        expected_params = {
            'input_token': 'foo_token',
            'access_token': 'app_id|secret',
        }

        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.endpoint, '/debug_token')
        self.assertEqual(request.graph_version, 'v2.12')
        self.assertDictEqual(request.params, expected_params)

    def test_get_authorization_url(self):
        oauth_client = OAuth2Client(app=self.app, client=None, graph_version='v2.12')
        scope = ['email', 'base_foo']
        params = {
            'foo': 'bar'
        }

        auth_url = oauth_client.get_authorization_url(
            redirect_url='https://foo.bar',
            params=params,
            state='foo_state',
            scope=scope,
        )

        expected_url = 'https://www.facebook.com/v2.12/dialog/oauth'
        self.assertIn(expected_url, auth_url)

        params = {
            'client_id': 'app_id',
            'redirect_uri': 'https://foo.bar',
            'state': 'foo_state',
            'sdk': 'facebook-python-sdk-{version}'.format(version=VERSION),
            'scope': ','.join(scope),
            'foo': 'bar',
            'response_type': 'code',
        }

        for k, v in params.items():
            self.assertIn('{k}={v}'.format(k=k, v=quote_plus(v)), auth_url)

    def test_get_long_lived_access_token(self):
        fb_client = FakeOAuth2Client(
            http_status_code=200,
            body='{"access_token":"my_access_token","expires":"1422115200"}',
            headers=[],
        )
        oauth_client = OAuth2Client(app=self.app, client=fb_client, graph_version='v2.12')
        long_live_access_token = oauth_client.get_long_lived_access_token(access_token='foo_token')

        self.assertIsInstance(long_live_access_token, AccessToken)
        self.assertEqual(str(long_live_access_token), 'my_access_token')

        request = oauth_client.last_request

        expected_params = {
            'access_token': 'app_id|secret',
            'client_secret': 'secret',
            'grant_type': 'fb_exchange_token',
            'client_id': 'app_id',
            'fb_exchange_token': 'foo_token'
        }

        self.assertDictEqual(request.params, expected_params)

    def test_get_access_token_from_code(self):
        fb_client = FakeOAuth2Client(
            http_status_code=200,
            body='{"access_token":"my_access_token","expires":"1422115200"}',
            headers=[],
        )
        oauth_client = OAuth2Client(app=self.app, client=fb_client, graph_version='v2.12')
        access_token = oauth_client.get_access_token_from_code(code='bar_code', redirect_uri='foo_uri')

        self.assertIsInstance(access_token, AccessToken)
        self.assertEqual(str(access_token), 'my_access_token')

        expected_params = {
            'code': 'bar_code',
            'redirect_uri': 'foo_uri',
            'access_token': 'app_id|secret',
            'client_id': 'app_id',
            'client_secret': 'secret',
        }

        request = oauth_client.last_request

        self.assertDictEqual(expected_params, request.params)

    def test_get_code_from_long_lived_access_token(self):
        fb_client = FakeOAuth2Client(
            http_status_code=200,
            body='{"code":"my_neat_code"}',
            headers=[],
        )
        oauth_client = OAuth2Client(app=self.app, client=fb_client, graph_version='v2.12')

        code = oauth_client.get_code_from_long_lived_access_token(
            access_token='long_access_token',
            redirect_uri='foo_uri'
        )

        self.assertEqual(code, 'my_neat_code')

        request = oauth_client.last_request
        expected_params = {
            'redirect_uri': 'foo_uri',
            'access_token': 'long_access_token',
            'client_id': 'app_id',
            'client_secret': 'secret',
        }

        self.assertEqual(request.endpoint, '/oauth/client_code')
        self.assertDictEqual(request.params, expected_params)
