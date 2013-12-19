# -*- coding: utf-8 -*-
"""
Backends tests suite.
"""
import unittest
from datetime import date

from presence_analyzer.cache.backends.base import MemoryBackend


class FooBar(object):
    """
    Example class
    """
    def __repr__(self):
        return '<class FooBar>'


# pylint: disable=E1103
class PresenceAnalyzerMemoryBackendTestCase(unittest.TestCase):
    """
    Memory backend tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        self.backend = MemoryBackend()

    def test_make_key(self):
        """
        Test make_key method.
        """
        args = ['fun', 'b', 'c']
        key = self.backend.make_key(args)
        self.assertEqual(key, 'fun_b_c')

        args = ['func_name', u'ż', u'ź', u'ć']
        key = self.backend.make_key(args)
        self.assertEqual(key, 'func_name_\xc5\xbc_\xc5\xba_\xc4\x87')

        args = ['func_name', 1.123]
        key = self.backend.make_key(args)
        self.assertEqual(key, 'func_name_1.123')

        args = ['func_name', FooBar()]
        key = self.backend.make_key(args)
        self.assertEqual(key, 'func_name_<class FooBar>')

        args = ['func_name', {FooBar(): 'test'}]
        key = self.backend.make_key(args)
        self.assertEqual(key, 'func_name_{<class FooBar>: \'test\'}')

        args = ['func_name', {u'ź': FooBar()}]
        key = self.backend.make_key(args)
        self.assertEqual(key, 'func_name_{u\'\\u017a\': <class FooBar>}')

        args = ['func_name', {date(2013, 12, 24): FooBar()}]
        key = self.backend.make_key(args)
        self.assertEqual(
            key,
            'func_name_{datetime.date(2013, 12, 24): <class FooBar>}'
        )


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerMemoryBackendTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
