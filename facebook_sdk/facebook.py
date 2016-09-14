from facebook_sdk.client import FacebookClient
from facebook_sdk.constants import DEFAULT_GRAPH_VERSION
from facebook_sdk.request import (
    FacebookBatchRequest,
    FacebookRequest,
)

class Facebook(object):
    def __init__(self):
        super(Facebook, self).__init__()
        self.client = FacebookClient()

    def request(self, method, endpoint, access_token=None, params=None, headers=None, graph_version=None):
        return FacebookRequest(
            method=method,
            access_token=access_token,
            endpoint=endpoint,
            params=params,
            headers=headers,
            graph_version=graph_version,
        )

    def send_request(self, method, endpoint, access_token=None, params=None, headers=None, graph_version=None):
        request = self.request(
            method=method,
            access_token=access_token,
            endpoint=endpoint,
            params=params,
            headers=headers,
            graph_version=graph_version or DEFAULT_GRAPH_VERSION,
        )
        response = self.client.send_request(request=request)

        return response

    def send_batch_request(self, requests, access_token=None, graph_version=None):

        batch_request = FacebookBatchRequest(
            requests=requests,
            access_token=access_token,
            graph_version=graph_version or DEFAULT_GRAPH_VERSION,
        )

        response = self.client.send_batch_request(batch_request=batch_request)
        return response
