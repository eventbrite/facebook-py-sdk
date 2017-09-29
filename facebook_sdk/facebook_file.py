import mimetypes
import os

from facebook_sdk.exceptions import FacebookSDKException


class FacebookFile(object):
    def __init__(self, path):
        super(FacebookFile, self).__init__()
        self.path = path
        if not os.path.exists(self.path):
            raise FacebookSDKException('File does not exist.')

    def read(self):
        """
        Override read to open, read and close fd after reading.
        """
        with open(self.path, mode='rb') as f:
            return f.read()

    @property
    def mime_type(self):
        return mimetypes.guess_type(self.path)[0]

    @property
    def name(self):
        return os.path.basename(self.path)
