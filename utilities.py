import datetime
import json
import unittest


def get_date_range_from_year_and_week(year: int, week: int) -> tuple:
    # reference: http://mvsourcecode.com/python-how-to-get-date-range-from-week-number-mvsourcecode/
    first = datetime.datetime.strptime(f'{year}-W{week - 1}-1', "%Y-W%W-%w").date()
    last = first + datetime.timedelta(days=6.9)
    return first, last


def load_credentials(config_filename: str) -> dict:
    # respects Inan's configuration
    with open(config_filename, 'r') as credentials:
        return json.load(credentials)

class TestISOWeek(unittest.TestCase):

    def test_first_week(self):
        first, last = get_date_range_from_year_and_week(2020, 1)
        self.assertEqual(first, datetime.date(2019, 12, 30))
        self.assertEqual(last, datetime.date(2020, 1, 5))

    def test_last_week(self):
        first, last = get_date_range_from_year_and_week(2019, 52)
        self.assertEqual(first, datetime.date(2019, 12, 23))
        self.assertEqual(last, datetime.date(2019, 12, 29))

    def test_leap_year(self):
        first, last = get_date_range_from_year_and_week(2020, 9)
        self.assertEqual(first, datetime.date(2020, 2, 24))
        self.assertEqual(last, datetime.date(2020, 3, 1))

class TestLoadSampleCredentials(unittest.TestCase):

    def test_sample_json(self):
        credentials = load_credentials('sample_credentials.json')
        self.assertEqual(credentials['jira_server'], 'YOUR_SERVER')
        self.assertEqual(credentials['jira_user'], 'YOUR_USERNAME')