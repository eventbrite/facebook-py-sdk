from facebook_sdk.exceptions import FacebookSDKException

MAX_REQUEST_BY_BATCH = 50

try:
    import simplejson as json
except ImportError:
    import json

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from facebook_sdk.constants import DEFAULT_GRAPH_VERSION, METHOD_POST
from facebook_sdk.utils import force_slash_prefix

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

        return urlencode(params) if params else None

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
            for key, req in request.items():
                self.add(req, key)
            return

        if not isinstance(request, FacebookRequest):
            raise FacebookSDKException('Arguments must be of type dict, list or FacebookRequest.')

        self.add_access_token(request)

        self.requests.append({
            'name': str(name),
            'request': request,
        })

    def add_access_token(self, request):
        if not request.access_token:
            access_token = self.access_token

            if not access_token:
                raise FacebookSDKException('Missing access token on FacebookRequest and FacebookBatchRequest')

            request.access_token = self.access_token

    def prepare_batch_request(self):
        params = {
            'batch': self.requests_to_json(),
            'include_headers': True,
        }
        self._params.update(params)

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

    def validate_batch_request_count(self):
        requests_count = len(self.requests)

        if not requests_count:
            raise FacebookSDKException('Empty batch requests')
        if requests_count > MAX_REQUEST_BY_BATCH:
            raise FacebookSDKException('The limit of requests in batch is {}'.format(MAX_REQUEST_BY_BATCH))

    def __iter__(self):
        return iter(self.requests)
