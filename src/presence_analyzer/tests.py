# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_mean_time_weekday(self):
        """
        Test mean time weekday view.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)

    def test_api_mean_time_weekday_fake(self):
        """
        Test mean time weekday view with fake user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/987')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

    def test_api_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0], [u'Weekday', u'Presence (s)'])

    def test_api_presence_weekday_fake(self):
        """
        Test presence weekday view with fake user.
        """
        resp = self.client.get('/api/v1/presence_weekday/987')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_seconds_since_midnight(self):
        """
        Test function calculates amount of seconds since midnight.
        """
        test_time = datetime.datetime(2013, 12, 12, 2, 30, 0)
        self.assertEqual(utils.seconds_since_midnight(test_time), 9000)

    def test_interval(self):
        """
        Test function calculates inverval in seconds between two
        datetime.time objects.
        """
        start = datetime.datetime(2013, 12, 12, 1, 29, 15)
        end = datetime.datetime(2013, 12, 12, 3, 30, 0)
        self.assertEqual(utils.interval(start, end), 7245)

    def test_mean(self):
        """
        Test calculates arithmetic mean.
        """
        items = [45682, 23434, 3457, 29940, 34532]
        self.assertEqual(utils.mean(items), 27409.0)

    def test_mean_zero_list(self):
        """
        Test calculates arithmetic mean if length of items equals zero.
        """
        items = []
        self.assertEqual(utils.mean(items), 0)

    def test_group_by_weekday(self):
        """
        Test groups presence entries by weekday.
        """
        weekday = [0, 1, 2, 3, 4, 5, 6]
        data = utils.get_data()
        result = utils.group_by_weekday(data[10])
        self.assertEqual(result.keys(), weekday)
        result = utils.group_by_weekday(data[11])
        self.assertEqual(result.keys(), weekday)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
