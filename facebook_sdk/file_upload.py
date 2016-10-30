import mimetypes
import os


class FacebookFile(object):
    def __init__(self, path):
        super(FacebookFile, self).__init__()
        self.path = path
        self._open()

    def _open(self):
        self.stream = open(self.path, mode='r')

    @property
    def mime_type(self):
        return mimetypes.guess_type(self.path)[0]

    @property
    def name(self):
        return os.path.basename(self.path)
