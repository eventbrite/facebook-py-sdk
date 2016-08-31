SUB_CODE_AUTH_EXCEPTION_CODES = (458, 459, 460, 463, 464, 467)
SUB_CODE_RESUMABLE_UPLOAD_EXCEPTION_CODES = (1363030, 1363030, 1363037, 1363033, 1363021, 1363041)
AUTH_EXCEPTION_CODES = (100, 102, 190)
SERVER_EXCEPTION_CODES = (1, 2)
THROTTLE_EXCEPTION_CODES = (4, 17, 341)
CLIENT_EXCEPTION_CODES = (506,)


class FacebookResponseException(Exception):
    def __init__(self, response, code, message, *args, **kwargs):
        super(FacebookResponseException, self).__init__(code, message)
        self.response = response

    @staticmethod
    def create(response):
        data = response.json_body

        if data.get('error', {}).get('code') is None and data.get('code') is not None:
            data = {'error': data}

        code = data.get('error').get('code')
        message = data.get('error').get('message') if data.get('error').get('message') else 'Unknown error from Graph.'
        sub_code = data.get('error').get('error_subcode')

        if sub_code:
            if sub_code in (SUB_CODE_AUTH_EXCEPTION_CODES):
                return FacebookAuthenticationException(response=response, code=code, message=message)
            if sub_code in (SUB_CODE_RESUMABLE_UPLOAD_EXCEPTION_CODES):
                return FacebookResumableUploadException(response=response, code=code, message=message)

        if code in AUTH_EXCEPTION_CODES:
            return FacebookAuthenticationException(response=response, code=code, message=message)
        if code in SERVER_EXCEPTION_CODES:
            return FacebookServerException(response=response, code=code, message=message)
        if code in THROTTLE_EXCEPTION_CODES:
            return FacebookThrottleException(response=response, code=code, message=message)

        if code == 10 or code >= 200 and code <= 299:
            return FacebookAuthorizationException(response=response, code=code, message=message)

        if data.get('error').get('type', None) == 'OAuthException':
            return FacebookAuthenticationException(response=response, code=code, message=message)

        return FacebookOtherException(response=response, code=code, message=message)


class FacebookAuthenticationException(FacebookResponseException):
    pass


class FacebookResumableUploadException(FacebookResponseException):
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
