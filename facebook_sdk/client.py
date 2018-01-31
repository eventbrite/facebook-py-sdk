try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import requests

from facebook_sdk.constants import BASE_GRAPH_URL, DEFAULT_REQUEST_TIMEOUT
from facebook_sdk.response import FacebookBatchResponse, FacebookResponse
from facebook_sdk.utils import convert_params_to_utf8


class FacebookClient(object):

    def __init__(self, request_timeout=None):
        self.timeout = request_timeout or DEFAULT_REQUEST_TIMEOUT

    def _prepareRequest(self, request):
        """

        :type request: FacebookRequest
        :rtype: tuple
        """
        url = BASE_GRAPH_URL + request.url

        data = None
        if request.contain_files():
            if request.post_params:
                # Content-Type form-data will be provided by requests lib
                data = request.post_params
        else:
            request.add_headers([
                {'Content-Type': 'application/x-www-form-urlencoded'},
            ])
            if request.post_params:
                data = urlencode(convert_params_to_utf8(request.post_params))

        return dict(
            url=url,
            method=request.method,
            params=request.params,
            data=data,
            headers=request.headers,
            files=request.files_to_upload(),
            timeout=request.timeout or self.timeout,
        )

    def send_request(self, request):
        """
        :type request: FacebookRequest
        :rtype: FacebookResponse
        """
        request_params = self._prepareRequest(request)

        res = self.send(
            **request_params
        )

        response = FacebookResponse(
            request=request,
            body=res.content,
            http_status_code=res.status_code,
        )

        if response.is_error:
            response.raiseException()

        return response

    def send(self, data, headers, method, params, url, files, timeout):
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            files=files,
            timeout=timeout,
        )
        return response

    def send_batch_request(self, batch_request):
        """
        :type batch_request: FacebookBatchRequest

        :rtype: FacebookBatchResponse
        """
        batch_request.validate_batch_request_count()
        batch_request.prepare_batch_request()
        batch_response = self.send_request(request=batch_request)

        response = FacebookBatchResponse(
            batch_request=batch_request,
            batch_response=batch_response,
        )

        return response
