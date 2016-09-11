import difflib
import pprint
from unittest import TestCase as UnitTestCase

from facebook_sdk.request import FacebookRequest, FacebookBatchRequest


def safe_repr(obj, short=False):
    """
    Helper class to provide backport support for `assertIn` and `assertIsInstance`
    for python 2.6
    """
    MAX_LENGTH = 80
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < MAX_LENGTH:
        return result
    return result[:MAX_LENGTH] + ' [truncated]...'


class TestCase(UnitTestCase):
    def assertIsInstance(self, obj, cls, msg=None):
        """ backward compatibility python2.6 """
        if not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictEqual(self, d1, d2, msg=None):
        """ backward compatibility python2.6 """
        self.assertIsInstance(d1, dict, 'First argument is not a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument is not a dictionary')

        if d1 != d2:
            standardMsg = '%s != %s' % (safe_repr(d1, True), safe_repr(d2, True))
            diff = ('\n' + '\n'.join(difflib.ndiff(
                pprint.pformat(d1).splitlines(),
                pprint.pformat(d2).splitlines())))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIn(self, member, container, msg=None):
        """ backward compatibility python2.6 """
        if member not in container:
            standardMsg = '%s not found in %s' % (safe_repr(member),
                                                  safe_repr(container))
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
