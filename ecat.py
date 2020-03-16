import argparse
import datetime

from jira import JIRA
from utilities import load_credentials, get_jira_date_string_from_datetime
from jira_utilities import get_datetime_from_property_holder, search_issue_history_for_property_dict, sort_issue_history_by_date
from my_transitions import active_development_transitions, inactive_development_transitions


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

        # get all transitions where work started
        # started_list = search_changelog(full_issue, [active_development_transitions.any_to_doing],
        #                                 sort_issue_history_by_date)
        #
        # # get all transitions where work stopped
        # stopped_list = search_changelog(full_issue, [inactive_development_transitions.any_to_blocked,
        #                                               inactive_development_transitions.any_to_icebox,
        #                                               inactive_development_transitions.doing_to_todo,
        #                                               inactive_development_transitions.test_to_verified,
        #                                               inactive_development_transitions.legacy_doing_to_done],
        #                                  sort_issue_history_by_date)

        status_changes = search_changelog(full_issue, [{'field' : 'status'}], sort_issue_history_by_date)

        build_transition_list(issue, status_changes)

        print(full_issue)
        print(f'has {len(status_changes)} status changes')
        #print(f'has {len(stopped_list)} stops')


def search_changelog(issue, property_dicts_to_match: list, sort_func: None) -> list:
    results_list = []

    for prop_dict in property_dicts_to_match:
        results_list = results_list + search_issue_history_for_property_dict(issue, prop_dict)

    if sort_func:
        results_list = sort_func(results_list)
    return results_list


def build_transition_list(issue, transitions) -> list:
    # return a list of tuples of the form:
    # (state, who, time spent in state)
    # first state is always 'open' with reporter as who
    transition_list = [('Open', issue.fields.reporter, None)]

    for transition in transitions:
        print(transition)

        # get only the status changes
        status_changes = search_issue_history_for_property_dict(transition.items, {'field' : 'status'})

        transition_list.append((transition.items[0].toString, transition.author, None))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show JIRA activity for a project by week for a year')
    parser.add_argument('--project', type=str, help='JIRA project name')
    parser.add_argument('--year', type=int, help='year to show')
    args = parser.parse_args()
    main(args)
