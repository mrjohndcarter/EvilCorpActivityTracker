import argparse

from datetime import date, datetime
from itertools import tee
from jira import JIRA
from jira_utilities import get_datetime_from_property_holder, recursive_search_for_property_dict
from utilities import load_credentials, get_jira_date_string_from_datetime


def main(args):
    creds = load_credentials('./private.json')
    jira = JIRA({"server": creds['jira_server']}, basic_auth=(creds['jira_user'], creds['jira_apikey']))

    jql_string = f'project = core AND status was DOING during ({get_jira_date_string_from_datetime(date(args.year, 1, 1))}, {get_jira_date_string_from_datetime(date(args.year, 12, 31))})'
    #jql_string = f'issue = US-11247'

    print(f'=* Evil Corp Activity Tracker *=')
    print(f'Query String: {jql_string}')

    issues_returned = jira.search_issues(jql_string)
    print(f'Yielded {len(issues_returned)} results')

    for issue in issues_returned:
        # fetch full issue
        full_issue = jira.issue(issue.key, expand='changelog', fields='assignee')

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

        history = build_history(issue, status_changes)

        print(full_issue)
        print(f'has {len(status_changes)} status changes')
        print(history)

def build_history(issue, status_change_tuples : list) -> list:
    # return a list of tuples of the form:
    # (state, who had it in this state, time spent in state)
    state_history = [];

    fromIt, ToIt = tee(status_change_tuples)

    # move to first state in list
    toState = next(ToIt) # get the first state we moved to

    # first state is always 'open' with reporter as who created it
    # open time is the time until someone touched it
    state_history.append(('Open', issue.fields.reporter.displayName , get_datetime_from_property_holder(toState[0]) - get_datetime_from_property_holder(issue.fields)));

    for toState in ToIt:
        fromState = next(fromIt)
        state_history.append((fromState[1][0].toString, fromState[0].author.displayName, get_datetime_from_property_holder(toState[0]) - get_datetime_from_property_holder(fromState[0])))

    # add final state, and time it has been in that state
    state_history.append((toState[1][0].toString, toState[0].author.displayName, datetime.now() - get_datetime_from_property_holder(toState[0])))

    return state_history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show JIRA activity for a project by week for a year')
    parser.add_argument('--project', type=str, help='JIRA project name')
    parser.add_argument('--year', type=int, help='year to show')
    args = parser.parse_args()
    main(args)
