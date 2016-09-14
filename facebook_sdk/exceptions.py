SUB_CODE_AUTH_EXCEPTION_CODES = (458, 459, 460, 463, 464, 467)
SUB_CODE_RESUMABLE_UPLOAD_EXCEPTION_CODES = (1363030, 1363030, 1363037, 1363033, 1363021, 1363041)
AUTH_EXCEPTION_CODES = (100, 102, 190)
SERVER_EXCEPTION_CODES = (1, 2)
THROTTLE_EXCEPTION_CODES = (4, 17, 341)
CLIENT_EXCEPTION_CODES = (506,)


class FacebookSDKException(Exception):
    pass


class FacebookRequestException(FacebookSDKException):
    pass


class FacebookResponseException(FacebookSDKException):
    def __init__(self, response, code, message, *args, **kwargs):
        super(FacebookResponseException, self).__init__(code, message)
        self.response = response

    @staticmethod
    def create(response):
        data = response.json_body
        error = (
            data
            if data.get('error', {}).get('code') is None and data.get('code') is not None
            else data.get('error', {})
        )

        code = error.get('code', -1)
        sub_code = error.get('error_subcode', -1)
        message = error.get('message', 'Unknown error from Graph.')

        if (
            sub_code in SUB_CODE_AUTH_EXCEPTION_CODES or
            code in AUTH_EXCEPTION_CODES or
            error.get('type') == 'OAuthException'
        ):
            exception = FacebookAuthenticationException
        elif sub_code in SUB_CODE_RESUMABLE_UPLOAD_EXCEPTION_CODES:
            exception = FacebookResumableUploadException
        elif code in SERVER_EXCEPTION_CODES:
            exception = FacebookServerException
        elif code in THROTTLE_EXCEPTION_CODES:
            exception = FacebookThrottleException
        elif code == 10 or 200 <= code <= 299:
            exception = FacebookAuthorizationException
        else:
            exception = FacebookOtherException

        return exception(response=response, code=code, message=message)


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
