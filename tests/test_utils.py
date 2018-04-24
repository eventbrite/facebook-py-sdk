# -*- coding: utf-8 -*-

from unittest import TestCase

from facebook_sdk.utils import smart_text


class TestFacebookFile(TestCase):

    def test_smart_text(self):
        test_scenarios = (
            (u'Beyoncé'.encode('utf-8'), u'Beyoncé'),
            (u'Beyoncé', u'Beyoncé'),
            (1, u'1'),
        )
        for value, expected in test_scenarios:
            self.assertEqual(smart_text(value), expected)
