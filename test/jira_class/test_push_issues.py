from unittest import mock

from fixtures import ISSUE_1
from jira_cli.main import Issue


def test_push_calls_load_issues(mock_jira):
    """
    Ensure Jira class calls load when no issues in self
    """
    mock_jira.load_issues = mock.Mock()
    mock_jira.push_issues()
    assert mock_jira.load_issues.called


def test_push_not_calls_load_issues(mock_jira):
    """
    Ensure Jira class doesn't call load when no issues in self
    """
    mock_jira.load_issues = mock.Mock()
    mock_jira['issue1'] = Issue.deserialize(ISSUE_1)
    mock_jira.push_issues()
    assert not mock_jira.load_issues.called


def test_push_does_sync_on_diff(mock_jira):
    """
    Ensure Jira class does sync the issue when issue.diff_to_upstream is set
    """
    mock_jira._sync_single_issue = mock.Mock()

    mock_jira['issue1'] = Issue.deserialize(ISSUE_1)
    mock_jira['issue1'].diff_to_upstream = {'not_a': 'real_diff'}
    mock_jira.push_issues()
    assert mock_jira._sync_single_issue.called


def test_push_does_not_sync_on_no_diff(mock_jira):
    """
    Ensure Jira class doesn't sync the issue when issue.diff_to_upstream is not set
    """
    mock_jira._sync_single_issue = mock.Mock()

    mock_jira['issue1'] = Issue.deserialize(ISSUE_1)
    mock_jira.push_issues()
    assert not mock_jira._sync_single_issue.called


def test__sync_single_issue(mock_jira):
    mock_jira['issue1'] = Issue.deserialize(ISSUE_1)

    # TODO add diff_to_upstream and test dictdiffer behaves a little
    # TODO add diff and then set upstream to orig; test sync
    # TODO add diff and set upstream to conflict; test sync
    pass
