import collections
import json
import urllib

import requests

BASE_GRAPH_URL = 'https://graph.facebook.com'

GRAPH_VERSION_V2_5 = 'v2.5'
GRAPH_VERSION_V2_6 = 'v2.6'
GRAPH_VERSION_V2_7 = 'v2.7'

DEFAULT_GRAPH_VERSION = GRAPH_VERSION_V2_5
DEFAULT_REQUEST_TIMEOUT = 60


METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_PUT = 'put'

def force_slash_prefix(value):
    return  value if value and str(value).endswith('/') else value + '/'


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
            graph_version=graph_version if graph_version else DEFAULT_GRAPH_VERSION,
        )
        response = self.client.send_request(request=request)

        return response

    def send_batch_request(self, batch_requests, access_token=None, graph_version=None):

        batch_request = FacebookBatchRequest(
            requests=batch_requests,
            access_token=access_token,
            graph_version=graph_version if graph_version else DEFAULT_GRAPH_VERSION,
        )

        response = self.client.send_batch_request(batch_request=batch_request)
        return response


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
        ( method, url, params, data, headers ) = self._prepareRequest(request)
        response = requests.request(method=method, url=url, headers=headers, params=params, data=urllib.urlencode(data), timeout=DEFAULT_REQUEST_TIMEOUT)

        # TODO: Build FacebookResponse
        return response

    def send_batch_request(self, batch_request):
        batch_request.prepare_batch_request()
        response = self.send_request(request=batch_request)

        return response


class FacebookRequest(object):

    def __init__(self, access_token=None, method=None, endpoint=None, params=None, headers=None, graph_version=None):
        super(FacebookRequest, self).__init__()

        # Default empty dicts for dict params.
        headers = {} if headers is None else headers
        params = {} if params is None else params
        graph_version = DEFAULT_GRAPH_VERSION if graph_version is None else graph_version

        self.access_token = access_token
        self.method = method
        self.endpoint = endpoint
        self.graph_version = graph_version
        self.headers = headers
        self._params = params

    @property
    def params(self):
        params = self._params.copy() if self.method != METHOD_POST else {}
        if self.access_token:
            params.update(dict(access_token=self.access_token))

        return params

    @property
    def post_params(self):
        if self.method == METHOD_POST:
            return self._params

        return None

    @property
    def url(self):
        return force_slash_prefix(self.graph_version) + force_slash_prefix(self.endpoint)


    @property
    def url_encode_body(self):
        params = self.post_params

        return urllib.urlencode(params) if params else None

    def add_headers(self, headers):
        for header in headers:
            self.headers.update(header)


class FacebookBatchRequest(FacebookRequest):

    def __init__(self, requests=None, access_token=None, graph_version=None):
        super(FacebookBatchRequest, self).__init__(access_token=access_token, graph_version=graph_version, method=METHOD_POST, endpoint='',)
        self.requests = []

        if requests:
            self.add(request=requests)

    def add(self, request, name=None):

        if isinstance(request, list):
            for index, req  in enumerate(request):
                self.add(req, index)
            return

        if isinstance(request, dict):
            for req, key in request.items():
                self.add(req, key)
            return

        self.add_access_token(request)

        self.requests.append({
            'name': str(name),
            'request': request,
        })

    def add_access_token(self, request):
        if not request.access_token:
            request.access_token = self.access_token

    def prepare_batch_request(self):
        params = {
            'batch': self.requests_to_json(),
            'include_headers': True,
        }
        self._params = params


    def request_entity_to_batch_array(self, request, request_name):

        batch = {
            'headers': request.headers,
            'method': request.method,
            'relative_url': request.url,
        }

        encoded_body = request.url_encode_body
        if encoded_body:
            batch['body'] = encoded_body

        if request_name is not None:
            batch['name'] = request_name

        if request.access_token != self.access_token:
            batch['access_token'] = request.access_token

        return batch

    def requests_to_json(self):
        json_requests = []
        for request in self.requests:
            json_requests.append(self.request_entity_to_batch_array(request=request['request'], request_name=request['name']))

        return json.dumps(json_requests)

    def __iter__(self):
        iter(self.requests)


class FacebookResponse(object):

    class FacebookResponseException(Exception):
        pass

    def __init__(self, request, body=None, http_status_code=None, headers=None):
        super(FacebookResponse, self).__init__()
        self.request = request
        self.body = body
        self.http_status_code = http_status_code
        self.headers = headers

        if self.is_error:
            self.build_exception()

    @property
    def is_error(self):
        return hasattr(self.body, 'error')

    def build_exeception(self):
        self.thrown_exception = FacebookResponseException()


class FacebookResponseException(Exception):

    def __init__(self, response, code, message, *args, **kwargs):
        super(FacebookResponseException, self).__init__(*args, **kwargs)
        self.response = response

    @staticmethod
    def create(response):
        data = response.body

        if data.get('error', {}).get('code') is None and data.get('code') is not None:
            data = {'error': data}




class FacebookAuthenticationException(FacebookResponseException):
    pass

class FacebookServerException(FacebookResponseException):
    pass

class FacebookThrottleException(FacebookResponseException):
    pass

class FacebookClientException(FacebookResponseException):
    pass

class FacebookAuthorizationException(FacebookResponseException):
    pass

class FacebookOtherException(FacebookResponseException):
    pass

class FacebookOfficialEventRequest(FacebookRequest):

    required_fields = ('category', 'cover', 'description', 'name', 'place_id', 'start_time', 'timezone')

    def __init__(self, event_id=None, *args, **kwargs):
        super(FacebookOfficialEventRequest, self).__init__(endpoint=event_id)

