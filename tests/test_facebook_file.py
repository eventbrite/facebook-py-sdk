import os
from unittest import TestCase

from facebook_sdk.exceptions import FacebookSDKException
from facebook_sdk.facebook_file import FacebookFile


class TestFacebookFile(TestCase):
    def setUp(self):
        super(TestFacebookFile, self).setUp()
        self.file_path = '{base_path}/foo.txt'.format(
            base_path=os.path.dirname(os.path.abspath(__file__)),
        )
        self.facebook_file = FacebookFile(path=self.file_path)

    def test_read(self):
        with open(self.file_path, mode='rb') as f:
            self.assertEqual(f.read(), self.facebook_file.read())

    def test_mime_type(self):
        self.assertTrue(self.facebook_file.mime_type, 'text/plain')

    def test_name(self):
        self.assertTrue(self.facebook_file.name, 'foo.txt')

    def test_file_does_not_exist(self):
        with self.assertRaises(FacebookSDKException):
            FacebookFile(
                path='does_not_exist.path',
            )
