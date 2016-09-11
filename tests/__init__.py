import difflib
import pprint
from unittest import TestCase as UnitTestCase
from unittest.util import safe_repr

from facebook_sdk.request import FacebookRequest, FacebookBatchRequest


class TestCase(UnitTestCase):
    def assertIsInstance(self, obj, cls, msg=None):
        """ backward compatibility python2.6
        """
        if getattr(self, "assertIsInstance", None):
            super(TestCase, self).assertIsInstance(obj, cls, msg)
        elif not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictEqual(self, d1, d2, msg=None):
        if getattr(self, "assertDictEqual", None):
            super(TestCase, self).assertDictEqual(d1, d2, msg)
        else:
            self.assertIsInstance(d1, dict, 'First argument is not a dictionary')
            self.assertIsInstance(d2, dict, 'Second argument is not a dictionary')

            if d1 != d2:
                standardMsg = '%s != %s' % (safe_repr(d1, True), safe_repr(d2, True))
                diff = ('\n' + '\n'.join(difflib.ndiff(
                    pprint.pformat(d1).splitlines(),
                    pprint.pformat(d2).splitlines())))
                standardMsg = self._truncateMessage(standardMsg, diff)
                self.fail(self._formatMessage(msg, standardMsg))


class FakeFacebookRequest(FacebookRequest):
    def __init__(self):
        super(FakeFacebookRequest, self).__init__(
            access_token='fake_token',
            method='get',
            endpoint='',
            params={},
            headers={},
            graph_version=None
        )


class FakeFacebookBatchRequest(FacebookBatchRequest):
    def __init__(self, requests):
        super(FakeFacebookBatchRequest, self).__init__(
            access_token='fake_token',
            requests=requests
        )
