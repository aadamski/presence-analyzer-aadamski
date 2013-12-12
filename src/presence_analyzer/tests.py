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

    def test_mainpage_redirect(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.headers['Location'].endswith('/presence_weekday.html')
        )

        resp = self.client.get('')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.headers['Location'].endswith('/presence_weekday.html')
        )

    def test_mainpage_view(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/presence_start_end.html')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)

    def test_mainpage_error(self):
        """
        Test raises error when page or resource not found
        """
        resp = self.client.get('/this_site_does_not_exist.html')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data, 'Not Found')

        resp = self.client.get('/favicon.ico')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data, 'Not Found')

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

    def test_api_mean_start_end(self):
        """
        Test groups presence entries by weekday.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data[0], [u'Mon', 0, 0])

    def test_api_bad_request(self):
        """
        Test error
        """
        resp = self.client.get('/api/v1/presence_start_end/')
        self.assertEqual(resp.status_code, 400)


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

    def test_group_by_weekday_start_end(self):
        """
        Test groups presence entries by weekday.
        """
        data = utils.get_data()
        result = utils.group_by_weekday_start_end(data[10])
        self.assertIsInstance(result, dict)
        self.assertEqual(result.keys(), range(7))
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[3], [38926.0, 62631.0])
        self.assertEqual(result[6], [0, 0])


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
