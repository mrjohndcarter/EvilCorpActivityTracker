import argparse
import csv
import json
import unittest
from _collections import defaultdict
from datetime import datetime, timedelta
from itertools import tee
from unittest.mock import Mock

from jira import JIRA


def main(args):
    with open(args.config, 'r') as credentials:
        creds = json.load(credentials)

    jira = JIRA({"server": creds['jira_server']}, basic_auth=(creds['jira_user'], creds['jira_apikey']))
    row_list = []

    print(f'=* Evil Corp Activity Tracker *=')
    print(f'Query String: {args.jql}')

    issues_returned = jira.search_issues(args.jql, maxResults=False)
    print(f' * Yielded {len(issues_returned)} results')
    print(f' * Processing ', end='')

    for issue in issues_returned:

        print('.', end='')

        # fetch full issue to expand changelog
        full_issue = jira.issue(issue.key, expand='changelog')

        # build the list of all status changes for this issue
        status_changes = []
        for property_holder in full_issue.changelog.histories:

            # for each entry in histories, see if we have any matches
            # this should always be 1, but i dunno.
            found_matches = recursive_search_for_property_dict(property_holder, {'field': 'status'})
            assert (len(found_matches) <= 1)

            # if have a match, add a tuple of top level property, and the status change found in its subtree
            if found_matches:
                status_changes.append((property_holder, found_matches))

        # sort status changes by date
        status_changes.sort(key=(lambda t: get_datetime_from_property_holder(t[0])))

        # from the build history (built from issue and queried status changes), aggregate maps of states -> times/who
        (states_with_time, states_with_who) = aggregate_states_from_history(build_history(issue, status_changes))

        hyperlink_item = f'=HYPERLINK("{args.prefix}/{issue.key} ", "{issue.key}")'

        row_list.append([hyperlink_item,
                         issue.fields.summary,
                         states_with_time['Doing'].days,
                         states_with_time['Test'].days,
                         ', '.join(states_with_who['Doing']),
                         ', '.join(states_with_who['Test'])])

    headers = ['Issue Link', 'Summary', 'Time in Doing (Days)', 'Time in Test (Days)', 'Who Worked on it (dev)',
               'Who Worked on it (test)']

    print(' * Writing')
    with open(args.output, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(row_list)
    print(' * Writing Complete')


def aggregate_states_from_history(history: list) -> (defaultdict, defaultdict):
    state_with_time = defaultdict(timedelta)
    state_with_who = defaultdict(list)
    for (state, name, delta) in history:
        state_with_time[state] = state_with_time[state] + delta
        state_with_who[state].append(name)
    return (state_with_time, state_with_who)


def build_history(issue, status_change_tuples: list) -> list:
    # return a list of tuples of the form:
    # (state, who had it in this state, time spent in state)
    state_history = [];

    fromIt, ToIt = tee(status_change_tuples)

    # move to first state in list
    toState = next(ToIt)  # get the first state we moved to

    # first state is always 'open' with reporter as who created it
    # open time is the time until someone touched it
    state_history.append(('Open', issue.fields.reporter.displayName,
                          get_datetime_from_property_holder(toState[0]) - get_datetime_from_property_holder(
                              issue.fields)));

    # construct sate from two adjacent transitions
    for toState in ToIt:
        fromState = next(fromIt)
        state_history.append((fromState[1][0].toString, fromState[0].author.displayName,
                              get_datetime_from_property_holder(toState[0]) - get_datetime_from_property_holder(
                                  fromState[0])))

    # add final state, and time it has been in that state (until now)
    state_history.append((toState[1][0].toString, toState[0].author.displayName,
                          datetime.now() - get_datetime_from_property_holder(toState[0])))

    return state_history


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


def get_jira_date_string_from_datetime(d: datetime) -> str:
    return d.strftime('%Y-%m-%d')


class TestGetJiraDate(unittest.TestCase):

    def test_from_datetime(self):
        self.assertEqual(get_jira_date_string_from_datetime(datetime.date(2020, 2, 24)), '2020-02-24')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Retrieve activity for a given JQL')
    parser.add_argument('jql', type=str, help='JQL query string'),
    parser.add_argument('--config', type=str,
                        help='JSON config file containing credentials (see sample_credentials.json)')
    parser.add_argument('--project', type=str, help='JIRA project name')
    parser.add_argument('--year', type=int, help='year to show')
    parser.add_argument('--prefix', type=str, help='Prefix URL for link to JIRA')
    parser.add_argument('--output', type=str, help='File to output csv to')
    args = parser.parse_args()
    main(args)
