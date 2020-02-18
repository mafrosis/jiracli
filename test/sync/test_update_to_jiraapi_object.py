'''
Tests for the issue_to_jiraapi_update function in sync module
'''
import pytest

from fixtures import ISSUE_1
from jira_cli.models import Issue
from jira_cli.sync import issue_to_jiraapi_update


@pytest.mark.parametrize('modified', [
    {'assignee'},
    {'fixVersions', 'summary'},
])
def test_issue_to_jiraapi_update__returns_only_fields_passed_in_modified(modified):
    '''
    Ensure issue_to_jiraapi_update returns only set of fields passed in modified parameter
    '''
    issue_dict = issue_to_jiraapi_update(Issue.deserialize(ISSUE_1), modified)
    assert issue_dict.keys() == modified


@pytest.mark.parametrize('modified', [
    {'assignee'},
    {'issuetype'},
    {'reporter'},
])
def test_issue_to_jiraapi_update__fields_are_formatted_correctly(modified):
    '''
    Ensure issue_to_jiraapi_update formats some fields correctly
    '''
    issue_dict = issue_to_jiraapi_update(Issue.deserialize(ISSUE_1), modified)
    assert 'name' in issue_dict[modified.pop()]


def test_issue_to_jiraapi_update__all_fields_are_returned_for_new_issue():
    '''
    Ensure issue_to_jiraapi_update returns all mandatory and new fields for a new Issue
    '''
    issue_dict = issue_to_jiraapi_update(
        Issue.deserialize(ISSUE_1),
        {'issuetype', 'project', 'summary', 'epic_ref', 'description', 'fixVersions', 'reporter'}
    )

    assert issue_dict == {
        'customfield_14182': 'TEST-1',
        'description': 'This is a story or issue',
        'fixVersions': ['0.1'],
        'issuetype': {'name': 'Story'},
        'project': {'key': 'TEST'},
        'reporter': {'name': 'danil1'},
        'summary': 'This is the story summary',
    }
