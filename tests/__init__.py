from facebook_sdk.client import FacebookClient
from facebook_sdk.request import FacebookRequest, FacebookBatchRequest
from facebook_sdk.response import FacebookResponse


class FakeFacebookClient(FacebookClient):
    def __init__(self, **kwargs):
        self.fake_response = kwargs.pop('fake_response')
        super(FakeFacebookClient, self).__init__(**kwargs)

    def send(self, *args, **kwargs):
        self.send_args = args,
        self.send_kwargs = kwargs
        return self.fake_response


class FakeOAuth2Client(FacebookClient):
    def __init__(self, body, http_status_code, headers):
        super(FakeOAuth2Client, self).__init__()
        self.body = body
        self.headers = headers
        self.http_status_code = http_status_code

    def send_request(self, request):
        return FacebookResponse(
            request=request,
            http_status_code=self.http_status_code,
            body=self.body,
            headers=self.headers,
        )


class FakeFacebookRequest(FacebookRequest):
    def __init__(self):
        super(FakeFacebookRequest, self).__init__(
            access_token='fake_token',
            method='get',
            endpoint='',
            params={},
            headers={},
            graph_version=None
        )


class FakeFacebookBatchRequest(FacebookBatchRequest):
    def __init__(self, requests):
        super(FakeFacebookBatchRequest, self).__init__(
            access_token='fake_token',
            requests=requests
        )


class FakeResponse(object):
    def __init__(self, content, headers, status_code):
        self.content = content
        self.headers = headers
        self.status_code = status_code
