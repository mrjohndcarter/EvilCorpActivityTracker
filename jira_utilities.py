from datetime import datetime


# I don't know enough about how JIRA stores its nested property lists to avoid the n*m complexity
def search_issue_history_for_property_dict(issue, match: dict):
    matches = []
    for property_holder in issue.changelog.histories:
        for item in property_holder.items:

            # filtering all items that are either missing or don't match
            def filter_function(_tuple):
                try:
                    return getattr(item, _tuple[0]) != _tuple[1]  # closed over item from outside scope
                except AttributeError:
                    return True

            # filter out all attributes that don't match
            iterator = filter(filter_function, match.items())

            if not dict(iterator):
                matches.append(property_holder)

    return matches


def get_datetime_from_property_holder(property_holder):
    # we don't care about ms, and strptime doesn't do well with offset timezones
    return datetime.strptime(property_holder.created.split('.')[0], "%Y-%m-%dT%H:%M:%S")


def sort_key_for_property_holder(property_holder):
    return get_datetime_from_property_holder(property_holder)


def sort_issue_history_by_date(history : list) -> list:
    return sorted(history, key=sort_key_for_property_holder)

