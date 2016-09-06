from facebook_sdk.request import FacebookRequest, FacebookBatchRequest


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