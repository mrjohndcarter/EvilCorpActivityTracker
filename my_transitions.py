class ActiveDevelopmentTransitions(object):
    @property
    def any_to_doing(self):
        return {'field': 'status',
                'toString': 'Doing'}


class InactiveDevelopmentTransitions(object):
    @property
    def any_to_blocked(self):
        return {'field': 'status',
                'toString': 'Blocked'}

    @property
    def any_to_icebox(self):
        return {'field': 'status',
                'toString': 'Ice Box'}

    @property
    def doing_to_todo(self):
        return {'field': 'status',
                'fromString': 'Doing',
                'toString': 'To Do'}
    @property
    def test_to_verified(self):
        return {'field': 'status',
                'fromString': 'Test',
                'toString': 'Verified'}

    @property
    def legacy_doing_to_done(self):
        return {'field': 'status',
                'fromString': 'Doing',
                'toString': 'Done'}

active_development_transitions = ActiveDevelopmentTransitions()
inactive_development_transitions = InactiveDevelopmentTransitions()