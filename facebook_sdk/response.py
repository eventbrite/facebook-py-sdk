from .exceptions import FacebookResponseException
class FacebookResponse(object):

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

    def build_exception(self):
        self.thrown_exception = FacebookResponseException.create(response=self)