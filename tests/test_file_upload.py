import os

from facebook_sdk.file_upload import FacebookFile
from tests import TestCase


class TestFacebook(TestCase):
    def setUp(self):
        super(TestFacebook, self).setUp()
        self.file_path='{base_path}/foo.txt'.format(
            base_path=os.path.dirname(os.path.abspath(__file__))
        )

    def test_file_is_open(self):
        facebook_file = FacebookFile(path=self.file_path)

        self.assertFalse(facebook_file.stream.closed)

    def test_file_mime_type(self):
        facebook_file = FacebookFile(path=self.file_path)

        self.assertTrue(facebook_file.mime_type, 'text/plain')

    def test_file_name(self):
        facebook_file = FacebookFile(path=self.file_path)

        self.assertTrue(facebook_file.name, 'foo.txt')

    def test_file_does_not_exist(self):
        self.assertRaises(
            IOError,
            FacebookFile,
            path='does_not_exist.path'
        )