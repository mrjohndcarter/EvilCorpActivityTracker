import datetime
import unittest


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
