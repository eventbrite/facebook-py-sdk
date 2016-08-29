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
