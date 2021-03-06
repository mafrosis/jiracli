ISSUE_1 = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'assignee': 'danil1',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': ['0.1'],
    'issuetype': 'Story',
    'id': '1231',
    'key': 'TEST-71',
    'labels': [],
    'priority': 'Normal',
    'reporter': 'danil1',
    'status': 'Story Done',
    'summary': 'This is the story summary',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'epic_ref': 'TEST-1',
    'diff_to_original': []
}

ISSUE_1_WITH_UPDATED_DIFF = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'assignee': 'danil1',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': ['0.1'],
    'issuetype': 'Story',
    'id': '1232',
    'key': 'TEST-71',
    'labels': [],
    'priority': 'Normal',
    'reporter': 'danil1',
    'status': 'Story Done',
    'summary': 'This is the story summary',
    'updated': '2000-08-20T00:00:00.000+10:00',
    'epic_ref': 'TEST-1',
    'diff_to_original': [('change', 'updated', ('2000-08-20T00:00:00.000+10:00', '2019-08-20T16:41:19+10:00'))]
}

ISSUE_1_WITH_PRIORITY_DIFF = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'assignee': 'danil1',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': ['0.1'],
    'issuetype': 'Story',
    'id': '1231',
    'key': 'TEST-71',
    'labels': [],
    'priority': 'Low',
    'reporter': 'danil1',
    'status': 'Story Done',
    'summary': 'This is the story summary',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'epic_ref': 'TEST-1',
    'diff_to_original': [('change', 'priority', ('Low', 'Normal'))]
}

ISSUE_1_WITH_ASSIGNEE_DIFF = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'assignee': 'hoganp',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': ['0.1'],
    'issuetype': 'Story',
    'id': '1233',
    'key': 'TEST-71',
    'labels': [],
    'priority': 'Normal',
    'reporter': 'danil1',
    'status': 'Story Done',
    'summary': 'This is the story summary',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'epic_ref': 'TEST-1',
    'diff_to_original': [('change', 'assignee', ('hoganp', 'danil1'))]
}

ISSUE_1_WITH_FIXVERSIONS_DIFF = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'assignee': 'danil1',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': ['0.1', '0.2'],
    'issuetype': 'Story',
    'id': '1234',
    'key': 'TEST-71',
    'labels': [],
    'priority': 'Normal',
    'reporter': 'danil1',
    'status': 'Story Done',
    'summary': 'This is the story summary',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'epic_ref': 'TEST-1',
    'diff_to_original': [('remove', 'fix_versions', [(1, '0.2')])]
}

ISSUE_2 = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'assignee': 'danil1',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': [],
    'issuetype': 'Story',
    'id': '1235',
    'key': 'TEST-72',
    'labels': [],
    'priority': 'Normal',
    'reporter': 'danil1',
    'status': 'Backlog',
    'summary': 'This is the story summary',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'epic_ref': 'TEST-1',
    'diff_to_original': []
}

ISSUE_MISSING_EPIC = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'description': 'This is a story or issue',
    'fix_versions': [],
    'issuetype': 'Story',
    'id': '1236',
    'key': 'TEST-73',
    'labels': [],
    'priority': 'Normal',
    'reporter': 'danil1',
    'status': 'Backlog',
    'summary': 'This is the story summary',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'diff_to_original': []
}

ISSUE_NEW = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'key': '7242cc9e-ea52-4e51-bd84-2ced250cabf0',
    'description': 'This is a story or issue',
    'issuetype': 'Story',
    'reporter': 'danil1',
    'summary': 'This is the story summary',
    'epic_ref': 'TEST-1',
    'fix_versions': ['0.1'],
}

EPIC_1 = {
    'project_id': '99fd9182cfc4c701a8a662f6293f4136201791b4',
    'created': '2018-09-24T08:44:06.000+10:00',
    'creator': 'danil1',
    'fix_versions': ['0.1'],
    'issuetype': 'Epic',
    'id': '2345',
    'key': 'TEST-1',
    'reporter': 'danil1',
    'status': 'Epic with Squad',
    'summary': 'This is an epic',
    'updated': '2019-08-20T16:41:19.000+10:00',
    'epic_name': '0.1: Epic about a thing',
    'diff_to_original': []
}
