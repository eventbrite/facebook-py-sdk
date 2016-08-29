import urllib
import requests

from facebook_sdk.constants import BASE_GRAPH_URL, DEFAULT_REQUEST_TIMEOUT
from facebook_sdk.utils import force_slash_prefix


class FacebookClient(object):

    def _prepareRequest(self, request):
        request.add_headers([
            {'Content-Type': 'application/x-www-form-urlencoded'}
        ])

        url = force_slash_prefix(BASE_GRAPH_URL) + request.url

        return (
            request.method,
            url,
            request.params,
            request.post_params,
            request.headers,
        )

    def send_request(self, request):
        (method, url, params, data, headers) = self._prepareRequest(request)

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=urllib.urlencode(data),
            timeout=DEFAULT_REQUEST_TIMEOUT
        )

        # TODO: Build FacebookResponse
        return response

    def send_batch_request(self, batch_request):
        batch_request.prepare_batch_request()
        response = self.send_request(request=batch_request)

        return response
