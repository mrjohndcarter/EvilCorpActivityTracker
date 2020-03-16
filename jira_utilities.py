from datetime import datetime

import unittest
from unittest.mock import Mock

def check_dict_match(item, match: dict) -> bool:
    for (k, v) in match.items():
        try:
            if getattr(item, k) != v:
                return False
        except AttributeError:
            return False
    return True


class TestDictMatch(unittest.TestCase):

    def testMatch(self):
        self.assertTrue(check_dict_match({}, {}))
        m = Mock()
        m.a = 'a'
        self.assertTrue(check_dict_match(m, {'a': 'a'}))
        m.b = 'b';
        self.assertTrue(check_dict_match(m, {'a': 'a'}))
        self.assertTrue(check_dict_match(m, {'a': 'a', 'b': 'b'}))

    def testDidNotMatch(self):
        m = Mock()
        m.a = 'b'
        self.assertFalse(check_dict_match(m, {'a': 'a'}))
        m.r = []
        self.assertFalse(check_dict_match(m, {'a': 'a'}))
        self.assertFalse(check_dict_match(m, {'missing': 'a'}))


# call it on a top level thing with items
def recursive_search_for_property_dict(top_level, match: dict) -> list:
    matches = []

    if check_dict_match(top_level, match):
        matches.append(top_level)

    # does the property holder have children (.items) ?
    if hasattr(top_level, 'items'):
        for property_holder in top_level.items:
            matches = matches + recursive_search_for_property_dict(property_holder, match)

    return matches


def get_datetime_from_property_holder(property_holder):
    # we don't care about ms, and strptime doesn't do well with offset timezones
    return datetime.strptime(property_holder.created.split('.')[0], "%Y-%m-%dT%H:%M:%S")

