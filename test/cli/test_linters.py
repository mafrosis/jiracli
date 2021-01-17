from unittest import mock

from click.testing import CliRunner
import pytest

from fixtures import ISSUE_1
from jira_offline.cli import cli
from jira_offline.jira import Issue


LINT_SUBCOMMANDS = [
    'fix-versions',
    'issues-missing-epic',
]


@pytest.mark.parametrize('subcommand', LINT_SUBCOMMANDS)
def test_lint_smoketest(mock_jira, subcommand):
    '''
    Dumb smoke test function to check for errors via CLI - when the jira-offline issue cache has a
    single issue
    '''
    # add fixture to Jira dict
    mock_jira['TEST-71'] = Issue.deserialize(ISSUE_1)

    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', subcommand])

    # CLI should always exit zero
    assert result.exit_code == 0


@pytest.mark.parametrize('subcommand', LINT_SUBCOMMANDS)
def test_lint_smoketest_empty(mock_jira, subcommand):
    '''
    Dumb smoke test function to check for errors via CLI - when the jira-offline issue cache is empty
    '''
    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', subcommand])

    # CLI should always exit 1
    assert result.exit_code == 1


@mock.patch('jira_offline.cli.linters.lint_fix_versions')
def test_cli_lint__fix_versions__echo(mock_lint_fix_versions, mock_jira):
    '''
    Ensure lint fix-versions command calls click.echo without error
    '''
    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', 'fix-versions'])

    assert result.exit_code == 0
    assert mock_lint_fix_versions.called
    assert result.output.endswith(' issues missing the fix_versions field\n')


@mock.patch('jira_offline.cli.linters.lint_fix_versions')
def test_cli_lint__fix_versions__fix_requires_words(mock_lint_fix_versions, mock_jira):
    '''
    Ensure lint fix-versions with --fix param errors without --value
    '''
    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', '--fix', 'fix-versions'])

    assert result.exit_code != 0
    assert result.output.endswith('You must pass --value with --fix\n')


@mock.patch('jira_offline.cli.linters.lint_fix_versions')
def test_cli_lint__fix_versions__fix_passes_words_to_lint_func(mock_lint_fix_versions, mock_jira):
    '''
    Ensure lint fix-versions with --fix and --value calls lint_fix_versions
    '''
    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', '--fix', 'fix-versions', '--value', '0.1'])

    assert result.exit_code == 0
    mock_lint_fix_versions.assert_called_with(mock_jira, fix=True, value='0.1')


@mock.patch('jira_offline.cli.linters.lint_issues_missing_epic')
def test_cli_lint__issues_missing_epic__echo(mock_lint_issues_missing_epic, mock_jira):
    '''
    Ensure lint issues_missing_epic command calls click.echo without error
    '''
    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', 'issues-missing-epic'])

    assert result.exit_code == 0
    assert mock_lint_issues_missing_epic.called
    assert result.output.endswith(' issues missing an epic\n')


@mock.patch('jira_offline.cli.linters.lint_issues_missing_epic')
def test_cli_lint__issues_missing_epic__fix_requires_epic_ref(mock_lint_issues_missing_epic, mock_jira):
    '''
    Ensure lint issues_missing_epic with --fix param errors without --epic-ref
    '''
    runner = CliRunner()
    result = runner.invoke(cli, ['lint', '--fix', 'issues-missing-epic'])
    assert result.exit_code != 0
    assert result.output.endswith('You must pass --epic_ref with --fix\n')


@mock.patch('jira_offline.cli.linters.lint_issues_missing_epic')
def test_cli_lint__issues_missing_epic__fix_passes_epic_ref_to_lint_func(mock_lint_issues_missing_epic, mock_jira):
    '''
    Ensure lint issues-missing-epic with --fix and --epic_ref calls lint_issues_missing_epic
    '''
    runner = CliRunner()

    with mock.patch('jira_offline.cli.linters.jira', mock_jira):
        result = runner.invoke(cli, ['lint', '--fix', 'issues-missing-epic', '--epic-ref', 'TEST'])

    assert result.exit_code == 0
    mock_lint_issues_missing_epic.assert_called_with(mock_jira, fix=True, epic_ref='TEST')
