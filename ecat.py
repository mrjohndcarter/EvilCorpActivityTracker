import argparse
import datetime

from jira import JIRA
from jira_utilities import get_datetime_from_property_holder, recursive_search_for_property_dict
from utilities import load_credentials, get_jira_date_string_from_datetime


def main(args):
    creds = load_credentials('./private.json')
    jira = JIRA({"server": creds['jira_server']}, basic_auth=(creds['jira_user'], creds['jira_apikey']))

    jql_string = f'project = core AND status was DOING during ({get_jira_date_string_from_datetime(datetime.date(args.year, 1, 1))}, {get_jira_date_string_from_datetime(datetime.date(args.year, 12, 31))})'

    print(f'=* Evil Corp Activity Tracker *=')
    print(f'Query String: {jql_string}')

    issues_returned = jira.search_issues(jql_string)
    print(f'Yielded {len(issues_returned)}')

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

        build_transition_list(issue, status_changes)

        print(full_issue)
        print(f'has {len(status_changes)} status changes')


def build_transition_list(issue, transitions) -> list:
    # return a list of tuples of the form:
    # (state, who, time spent in state)
    # first state is always 'open' with reporter as who
    transition_list = [('Open', issue.fields.reporter, None)]

    for transition in transitions:
        print(transition)

        # get only the status changes
        # status_changes = search_issue_itemlist_for_property_dict(transition, {'field' : 'status'})
        status_changes = recursive_search_for_property_dict(transition, {'field': 'status'})

        # transition_list.append((transition.items[0].toString, transition.author, None))

    return transition_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show JIRA activity for a project by week for a year')
    parser.add_argument('--project', type=str, help='JIRA project name')
    parser.add_argument('--year', type=int, help='year to show')
    args = parser.parse_args()
    main(args)
