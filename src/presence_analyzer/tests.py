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
        msg = u'%s element (%s) of list is not an instance of %s'
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        for index in range(7):
            self.assertIsInstance(
                data[index][0],
                unicode,
                msg % (index, type(data[index][0]), u'unicode')
            )
            self.assertIsInstance(
                data[index][1],
                float,
                msg % (index, type(data[index][0]), u'float')
            )

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
        msg = u'%s element (%s) of list is not an instance of %s'
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertIsInstance(data, list)
        self.assertEqual(data[0], [u'Weekday', u'Presence (s)'])
        for index in range(1, 8):
            self.assertIsInstance(
                data[index][0],
                unicode,
                msg % (index, type(data[index][0]), u'unicode')
            )
            self.assertIsInstance(
                data[index][1],
                int,
                msg % (index, type(data[index][1]), u'int')
            )

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
        test_zero = datetime.datetime(2013, 12, 12, 0, 0, 0)
        test_time = datetime.datetime(2013, 12, 12, 2, 30, 0)
        test_max = datetime.datetime(2013, 12, 13, 23, 59, 59)
        self.assertEqual(utils.seconds_since_midnight(test_zero), 0)
        self.assertEqual(utils.seconds_since_midnight(test_time), 9000)
        self.assertEqual(utils.seconds_since_midnight(test_max), 86399)

    def test_interval(self):
        """
        Test function calculates inverval in seconds between two
        datetime.time objects.
        """
        test_values = [
            ([
                datetime.datetime(2013, 12, 12, 1, 29, 15),
                datetime.datetime(2013, 12, 12, 3, 30, 0)
            ], 7245),
            ([
                datetime.datetime(2013, 12, 12, 0, 0, 0),
                datetime.datetime(2013, 12, 12, 0, 0, 0)
            ], 0),
            ([
                datetime.datetime(2013, 12, 12, 0, 0, 0),
                datetime.datetime(2013, 12, 12, 23, 59, 59)
            ], 86399)
        ]
        self.assertEqual(
            utils.interval(test_values[0][0][0], test_values[0][0][1]),
            test_values[0][1]
        )
        self.assertEqual(
            utils.interval(test_values[1][0][0], test_values[1][0][1]),
            test_values[1][1]
        )
        self.assertEqual(
            utils.interval(test_values[2][0][0], test_values[2][0][1]),
            test_values[2][1]
        )

    def test_mean(self):
        """
        Test calculates arithmetic mean.
        """
        test_values = [
            ([0, 0, 0], 0),
            ([0, 86399], 43199.5),
            ([86399, 86399, 86399, 86399], 86399.0),
            ([45682, 23434, 3457, 29940, 34532], 27409.0),
            ([0, 244, 3214, 21568, 5410, 5120], 5926.0),
            ([6548, 54884, 2215, 32654, 21545, 1230], 19846.0),
        ]
        self.assertEqual(utils.mean(test_values[0][0]), test_values[0][1])
        self.assertEqual(utils.mean(test_values[1][0]), test_values[1][1])
        self.assertEqual(utils.mean(test_values[2][0]), test_values[2][1])
        self.assertEqual(utils.mean(test_values[3][0]), test_values[3][1])
        self.assertEqual(utils.mean(test_values[4][0]), test_values[4][1])
        self.assertEqual(utils.mean(test_values[5][0]), test_values[5][1])

    def test_mean_zero_list(self):
        """
        Test calculates arithmetic mean if length of items equals zero.
        """
        items = []
        self.assertEqual(utils.mean(items), 0.0)

    def test_group_by_weekday(self):
        """
        Test groups presence entries by weekday.
        """
        data = utils.get_data()
        result = utils.group_by_weekday(data[11])
        self.assertEqual(result.keys(), range(7))
        self.assertEqual(result[0], [24123])
        self.assertEqual(result[1], [16564])
        self.assertEqual(result[2], [25321])
        self.assertEqual(result[3], [22969, 22999])


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
