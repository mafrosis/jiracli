from unittest import mock

from jira_cli.main import Issue
from jira_cli.linters import issues_missing_epic
from test.fixtures import ISSUE_2, ISSUE_3


@mock.patch('jira_cli.linters.Jira')
def test_lint_issues_missing_epic_finds_issues_missing_epic(mock_jira_local, mock_jira):
    '''
    Ensure CLI lint issues_missing_epic command returns Issues missing the epic_ref field
    '''
    # add fixtures to Jira dict
    mock_jira['issue1'] = Issue.deserialize(ISSUE_2)
    mock_jira['issue3'] = Issue.deserialize(ISSUE_3)

    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    # assert two issues in Jira
    assert len(mock_jira.df) == 2

    df = issues_missing_epic(fix=False)

    # assert single issue missing an epic
    assert len(df) == 1


@mock.patch('jira_cli.linters.Jira')
def test_lint_issues_missing_epic_fix_updates_an_issue(mock_jira_local, mock_jira):
    '''
    Ensure CLI lint issues_missing_epic command sets epic_ref of an issue when fix=True
    '''
    # add fixtures to Jira dict
    mock_jira['issue1'] = Issue.deserialize(ISSUE_2)
    mock_jira['issue3'] = Issue.deserialize(ISSUE_3)

    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    # assert issue3 has an empty epic_ref
    assert mock_jira['issue3'].epic_ref is None

    df = issues_missing_epic(fix=True, epic_ref='EGG-1234')

    # assert no issues missing an epic
    assert len(df) == 0
    # assert issue3's epic_ref has been updated
    assert mock_jira['issue3'].epic_ref == 'EGG-1234'
    # ensure changes written to disk
    assert mock_jira.write_issues.called