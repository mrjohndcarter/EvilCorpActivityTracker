from datetime import datetime


# I don't know enough about how JIRA stores its nested property lists to avoid the n*m complexity
def search_issue_history_for_property_change(issue, field_changed: str, from_value: str, to_value: str):
    matches = []
    for property_holder in issue.changelog.histories:
        for item in property_holder.items:
            print(getattr(item, 'field'))
            if item.field == field_changed and item.fromString == from_value and item.toString == to_value:
                matches.append(property_holder)
    return matches


def search_issue_history_for_property_dict(issue, match: dict):
    matches = []
    for property_holder in issue.changelog.histories:
        for item in property_holder.items:
            # filtering all items that are either missing or don't match
            # should probably short circuit this and not use filter
            def filter_function(_tuple):
                try:
                    return getattr(item, _tuple[0]) != _tuple[1] # closed over item from outside scope
                except AttributeError:
                    return True

            # filter out all attributes that don't match
            iterator = filter(filter_function, match.items())

            if (len(dict(iterator))) == 0:
                matches.append(property_holder)

    return matches


def get_datetime_from_property_holder(property_holder):
    # we don't care about ms, and strptime doesn't do well with offset timezones
    return datetime.strptime(property_holder.created.split('.')[0], "%Y-%m-%dT%H:%M:%S")
