import datetime
import json
import unittest
from time import strptime


def get_date_range_from_year_and_week(year: int, week: int) -> tuple:
    # reference: http://mvsourcecode.com/python-how-to-get-date-range-from-week-number-mvsourcecode/
    first = datetime.datetime.strptime(f'{year}-W{week - 1}-1', "%Y-W%W-%w").date()
    last = first + datetime.timedelta(days=6.9)
    return first, last


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


def load_credentials(config_filename: str) -> dict:
    # respects Inan's configuration
    with open(config_filename, 'r') as credentials:
        return json.load(credentials)


class TestLoadSampleCredentials(unittest.TestCase):

    def test_sample_json(self):
        credentials = load_credentials('sample_credentials.json')
        self.assertEqual(credentials['jira_server'], 'YOUR_SERVER')
        self.assertEqual(credentials['jira_user'], 'YOUR_USERNAME')


# not that good, but we'll see what we need
def build_jql_string_from_dict(parameters: dict, boolean: str = 'AND', operator: str = '=') -> str:
    return f' {boolean} '.join([f'{k} {operator} {v}' for (k, v) in parameters.items()])


class TestBuildJQLString(unittest.TestCase):

    def test_defaults(self):
        self.assertEqual(build_jql_string_from_dict({'project': 'pizza', 'feature': 'toppings'}),
                         'project = pizza AND feature = toppings')

    def test_args(self):
        self.assertEqual(build_jql_string_from_dict({'project': 'pizza', 'issue': '10000'}, 'OR', '>'),
                         'project > pizza OR issue > 10000')

    def test_compose(self):
        self.assertEqual(' AND '.join([build_jql_string_from_dict({'project': 'pizza', 'feature': 'toppings'}),
                                       build_jql_string_from_dict({'cost': '100', 'price': '200'}, 'OR', '>')]),
                         'project = pizza AND feature = toppings AND cost > 100 OR price > 200')


def get_jira_date_string_from_datetime(d: datetime) -> str:
    return d.strftime('%Y-%m-%d')


class TestGetJiraDate(unittest.TestCase):

    def test_from_datetime(self):
        self.assertEqual(get_jira_date_string_from_datetime(datetime.date(2020, 2, 24)), '2020-02-24')

