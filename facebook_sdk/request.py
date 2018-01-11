import uuid

from facebook_sdk.facebook_file import FacebookFile


try:
    import simplejson as json
except ImportError:
    import json

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from facebook_sdk.constants import DEFAULT_GRAPH_VERSION, METHOD_POST
from facebook_sdk.exceptions import FacebookSDKException
from facebook_sdk.utils import (
    convert_params_to_utf8,
    force_slash_prefix,
    get_params_from_url,
    remove_params_from_url,
)

MAX_REQUEST_BY_BATCH = 50


class FacebookRequest(object):
    """ A Facebook Request.

    """

    def __init__(self, app=None, access_token=None, method=None, endpoint=None, params=None, headers=None,
                 graph_version=None, timeout=None):
        super(FacebookRequest, self).__init__()

        # Default empty dicts for dict params.
        headers = headers or {}
        params = params or {}
        graph_version = graph_version or DEFAULT_GRAPH_VERSION

        self.app = app
        self.access_token = access_token
        self.method = method
        self.endpoint = endpoint
        self.graph_version = graph_version
        self.headers = headers
        self.params = params
        self.timeout = timeout

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value):
        params = get_params_from_url(value)
        if params.get('access_token'):
            access_token = ''.join(params.get('access_token'))
            if not self.access_token:
                self.access_token = access_token
            elif self.access_token != access_token:
                raise FacebookSDKException(
                    'Access token mismatch. The access token provided in the FacebookRequest '
                    'and the one provided in the URL or POST params do not match.'
                )

        self._endpoint = remove_params_from_url(value, params_to_remove=['access_token', 'appsecret_proof'])

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        if value:
            self._access_token = str(value)
        else:
            self._access_token = None

    @property
    def params(self):
        """ The url params.

        :rtype: dict
        """
        params = self._params.copy() if self.method != METHOD_POST else {}
        if self.access_token:
            params.update(dict(access_token=self.access_token))

        return params

    @params.setter
    def params(self, value):
        if 'access_token' in value:
            self.access_token = value.get('access_token')

        value.pop('access_token', None)
        value.pop('appsecret_proof', None)

        self._extract_files_from_params(value)
        self._params = getattr(self, '_params', {})
        self._params.update(value)

    @property
    def post_params(self):
        """ The post params.

        :rtype: object
        """
        if self.method == METHOD_POST:
            return self._params.copy()

        return None

    @property
    def url(self):
        """ The relative url to the graph api.

        :rtype: str
        """
        return force_slash_prefix(self.graph_version) + force_slash_prefix(self.endpoint)

    @property
    def batch_url(self):
        """ The relative url to the graph api.

        :rtype: str
        """
        params = self.params
        url = self.url

        if self.method != METHOD_POST and params:
            return '{url}?{encoded_params}'.format(url=url, encoded_params=urlencode(convert_params_to_utf8(self.params)))

        return url

    @property
    def url_encode_body(self):
        """ Convert the post params to a urlencoded str

        :rtype: str
        """
        params = self.post_params

        if not params:
            return None

        return urlencode(convert_params_to_utf8(params))

    def add_headers(self, headers):
        """ Append headers to the request.

        :param headers: a list of headers
        """
        for header in headers:
            self.headers.update(header)

    def _extract_files_from_params(self, value):
        self.files = {}
        for k, v in value.items():
            if isinstance(v, FacebookFile):
                self.files[k] = v

        for k in self.files.keys():
            value.pop(k)

    def contain_files(self):
        return bool(self.files)

    def files_to_upload(self):
        return [(name, (_file.name, _file, _file.mime_type)) for name, _file in self.files.items()]


class FacebookBatchRequest(FacebookRequest):
    """ A Facebook Batch Request.

    """

    def __init__(self, app=None, requests=None, access_token=None, graph_version=None, timeout=None):
        """
        :param requests: a list of FacebookRequest
        :param access_token: the access token for the batch request
        :param graph_version: the graph version for the batch request
        """
        graph_version = graph_version or DEFAULT_GRAPH_VERSION

        super(FacebookBatchRequest, self).__init__(
            app=app,
            access_token=access_token,
            graph_version=graph_version,
            method=METHOD_POST,
            endpoint='',
            timeout=timeout,
        )

        self.requests = []

        if requests:
            self.add(request=requests)

    def add(self, request, name=None):
        """ Append a request or a set of requests to the batches.

        :param request: an instance, list or dict of FacebookRequest
        :param name: the name of the request. keep it as None if you provide a set of requests
        """

        if isinstance(request, list):
            for index, req in enumerate(request):
                self.add(req, index)
            return

        if isinstance(request, dict):
            for key, req in request.items():
                self.add(req, key)
            return

        if not isinstance(request, FacebookRequest):
            raise FacebookSDKException('Arguments must be of type dict, list or FacebookRequest.')

        self._add_access_token(request)

        request_to_add = {
            'name': str(name),
            'request': request,
        }

        attached_files = self.extract_file_attachments(request)
        if attached_files:
            request_to_add['attached_files'] = attached_files

        self.requests.append(request_to_add)

    def _add_access_token(self, request):
        """ Set the batch request access token to the request if it wasn't provided.

        :type request: FacebookRequest
        """

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

    def request_entity_to_batch_array(self, request, request_name, attached_files):
        """ Convert a FacebookRequest entity to a request batch representation.

        :param request: a FacebookRequest
        :param request_name: the request name
        :return: a dict with the representation of the request
        """

        batch = {
            'headers': request.headers,
            'method': request.method,
            'relative_url': request.batch_url,
        }

        encoded_body = request.url_encode_body
        if encoded_body:
            batch['body'] = encoded_body

        if request_name is not None:
            batch['name'] = request_name

        if request.access_token != self.access_token:
            batch['access_token'] = request.access_token

        if attached_files:
            batch['attached_files'] = attached_files

        return batch

    def requests_to_json(self):
        """ Convert the requests to json."""
        json_requests = [
            self.request_entity_to_batch_array(
                request_name=request.get('name'),
                request=request.get('request'),
                attached_files=request.get('attached_files'),
            ) for request in self.requests
        ]

        return json.dumps(json_requests)

    def validate_batch_request_count(self):
        """ Validate the request count before sending them as a batch.

            :raise FacebookSDKException
        """
        requests_count = len(self.requests)

        if not requests_count:
            raise FacebookSDKException('Empty batch requests')
        if requests_count > MAX_REQUEST_BY_BATCH:
            raise FacebookSDKException('The limit of requests in batch is %d' % MAX_REQUEST_BY_BATCH)

    def extract_file_attachments(self, request):
        """ Remove files from the request and return file names removed
        :param request:
        :return:
        """
        file_names = []
        for _file in request.files.values():
            file_name = uuid.uuid4().hex
            self.files[file_name] = _file
            file_names.append(file_name)

        request.files.clear()

        return ','.join(file_names)

    def __iter__(self):
        return iter(self.requests)
