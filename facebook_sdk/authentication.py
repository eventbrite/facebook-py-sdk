import datetime
import hashlib
import hmac

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from facebook_sdk.exceptions import FacebookSDKException

from facebook_sdk import __VERSION__ as VERSION
from facebook_sdk import constants
from facebook_sdk.client import FacebookClient
from facebook_sdk.request import FacebookRequest


class AccessToken(object):
    def __init__(self, access_token, expires_at=None):
        super(AccessToken, self).__init__()

        self.access_token = access_token

        if expires_at:
            self.expires_at = expires_at

    def app_secret_proof(self, secret):
        return hmac.new(bytes(secret.encode('utf-8')), self.access_token.encode('utf-8'), hashlib.sha256).hexdigest()

    def is_app_access_token(self):
        return len(self.access_token.split('|')) == 2

    def is_long_lived(self):
        if getattr(self, 'expires_at', None):
            return self.expires_at > datetime.datetime.utcnow() + datetime.timedelta(hours=2)

        return self.is_app_access_token()

    def is_expired(self):
        if getattr(self, 'expires_at', None):
            return self.expires_at < datetime.datetime.utcnow()

        return False

    def __str__(self):
        return self.access_token


class OAuth2Client(object):
    def __init__(self, app, client, graph_version=None):
        """
        :type app: FacebookApp
        :type client: FacebookClient
        :type graph_version: str
        """
        super(OAuth2Client, self).__init__()
        self.app = app
        self.client = client
        self.graph_version = graph_version or constants.DEFAULT_GRAPH_VERSION

    def get_authorization_url(self, redirect_url, state, scope=None, params=None):
        """ Generates an authorization URL to begin the process of authenticating a user.

        :param redirect_url The callback URL to redirect to.
        :param scope        A list of permissions to request.
        :param state        The CSPRNG-generated CSRF value.
        :param params       a dict of parameters to generate URL.

        :type params: dict
        :type scope: list
        :type state: str
        :type redirect_url: str
        """
        scope = scope or []
        params = params or {}

        params.update({
            'client_id': self.app.id,
            'state': state,
            'response_type': 'code',
            'sdk': 'facebook-python-sdk-{version}'.format(version=VERSION),
            'redirect_uri': redirect_url,
            'scope': ','.join(scope),
        })

        return '{base_url}/{graph_version}/dialog/oauth?{query}'.format(
            base_url=constants.BASE_AUTHORIZATION_URL,
            graph_version=self.graph_version,
            query=urlencode(params)
        )

    def debug_token(self, access_token):
        """
        https://developers.facebook.com/docs/graph-api/reference/v2.8/debug_token

        :param access_token:

        :raise FacebookSDKException

        :return: the token metadata
        """
        params = {
            'input_token': str(access_token)
        }

        self.last_request = FacebookRequest(
            app=self.app,
            access_token=self.app.access_token(),
            method='GET',
            endpoint='/debug_token',
            params=params,
            graph_version=self.graph_version,
        )

        response = self.client.send_request(self.last_request)

        return response.json_body

    def get_access_token_from_code(self, code, redirect_uri=''):
        params = {
            'code': code,
            'redirect_uri': redirect_uri
        }

        return self._request_an_access_token(params=params)

    def get_long_lived_access_token(self, access_token):
        """ Exchanges a short-lived access token with a long-lived access token.

        :param access_token:

        :raise FacebookSDKException

        :return an AccessToken
        """
        params = {
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': str(access_token),
        }

        return self._request_an_access_token(params=params)

    def get_code_from_long_lived_access_token(self, access_token, redirect_uri):
        params = {
            'redirect_uri': redirect_uri,
        }

        response = self._send_request_with_client_params(
            '/oauth/client_code',
            params=params,
            access_token=access_token,
        )

        data = response.json_body

        if not data.get('code'):
            raise FacebookSDKException('Code was not returned from Graph.', 401);

        return data.get('code')

    def _send_request_with_client_params(self, endpoint, params, access_token=None):
        """
        :type endpoint: str
        :type params: dict
        :type access_token: str

        :return FacebookResponse
        """
        params.update(self._get_client_params())

        access_token = access_token or self.app.access_token()

        self.last_request = FacebookRequest(
            app=self.app,
            access_token=str(access_token),
            method='GET',
            endpoint=endpoint,
            params=params,
            graph_version=self.graph_version,
        )

        return self.client.send_request(self.last_request)

    def _get_client_params(self):
        return {
            'client_id': self.app.id,
            'client_secret': self.app.secret
        }

    def _request_an_access_token(self, params):
        response = self._send_request_with_client_params(
            endpoint='/oauth/access_token',
            params=params,
        )
        data = response.json_body

        if not data.get('access_token'):
            raise FacebookSDKException('Access token was not returned from Graph.', 401)

        # For exchanging a short lived token with a long lived token.
        # The expiration time in seconds will be returned as "expires".
        expires_at = None
        if data.get('expires'):
            expires_at = datetime.datetime.utcfromtimestamp(int(data.get('expires')))
        elif data.get('expires_in'):
            # For exchanging a code for a short lived access token.
            # The expiration time in seconds will be returned as "expires_in".
            # See: https://developers.facebook.com/docs/facebook-login/access-tokens#long-via-code
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=(data.get('expires_in')))

        return AccessToken(
            access_token=data.get('access_token'),
            expires_at=expires_at
        )
