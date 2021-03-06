import json
import logging
from unittest import mock

import click
from click.testing import CliRunner
import pytest

from fixtures import ISSUE_1, ISSUE_NEW
from jira_offline.cli import cli
from jira_offline.jira import Issue


@mock.patch('jira_offline.cli.Jira')
def test_verbose_flag_sets_logger_to_info_level(mock_jira_local, mock_jira):
    '''
    Ensure the --verbose flag correctly sets the logger level
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    runner = CliRunner()
    runner.invoke(cli, ['--verbose', 'show'])
    assert logging.getLogger('jira').level == logging.INFO


@mock.patch('jira_offline.cli.Jira')
def test_debug_flag_sets_logger_to_debug_level(mock_jira_local, mock_jira):
    '''
    Ensure the --debug flag correctly sets the logger level
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    runner = CliRunner()
    runner.invoke(cli, ['--debug', 'show'])
    assert logging.getLogger('jira').level == logging.DEBUG


@mock.patch('jira_offline.cli.Jira')
def test_cli_show_invalid_issue_key(mock_jira_local, mock_jira):
    '''
    Ensure show command errors when passed an invalid/missing Issue key
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    runner = CliRunner()
    result = runner.invoke(cli, ['show', 'TEST-71'])
    assert result.exit_code == 1
    assert result.output == 'Unknown issue key\nAborted!\n'


@pytest.mark.parametrize('command,params', [
    ('show', ('--json', 'TEST-71')),
    ('new', ('--json', 'TEST', 'Story', 'Summary of issue')),
    ('edit', ('--json', 'TEST-71', '--summary', 'A new summary')),
])
@mock.patch('jira_offline.cli.Jira')
def test_cli_commands_can_return_json(mock_jira_local, mock_jira, command, params):
    '''
    Ensure show command can return output as JSON
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    # add fixture to Jira dict
    mock_jira['TEST-71'] = Issue.deserialize(ISSUE_1)

    runner = CliRunner()
    result = runner.invoke(cli, [command, *params])
    assert result.exit_code == 0
    try:
        json.loads(f'{result.output}')
    except json.decoder.JSONDecodeError:
        pytest.fail('Invalid JSON returned!')


@mock.patch('jira_offline.cli.main.pull_issues')
@mock.patch('jira_offline.cli.Jira')
def test_cli_pull_reset_hard_flag_calls_confirm_abort(mock_jira_local, mock_pull_issues, mock_jira):
    '''
    Ensure pull --reset-hard calls click.confirm() with abort=True flag
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    click.confirm = mock_click_confirm = mock.Mock(side_effect=click.exceptions.Abort)

    runner = CliRunner()
    runner.invoke(cli, ['pull', '--reset-hard'])
    assert mock_click_confirm.called
    assert mock_click_confirm.call_args_list[0][1] == {'abort': True}
    assert not mock_pull_issues.called


@mock.patch('jira_offline.cli.Jira')
def test_cli_new_error_when_passed_project_not_in_config(mock_jira_local, mock_jira):
    '''
    Ensure an error happens when the passed --project is missing from config.projects
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    runner = CliRunner()
    result = runner.invoke(cli, ['new', 'EGG', 'Story', 'Summary of issue'])
    assert result.exit_code == 1
    assert not mock_jira.new_issue.called


@mock.patch('jira_offline.cli.Jira')
def test_cli_new_error_when_not_passed_epic_name_for_epic(mock_jira_local, mock_jira):
    '''
    Ensure an error happens when --epic-name is not passed for Epic creation
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    runner = CliRunner()
    result = runner.invoke(cli, ['new', 'TEST', 'Epic', 'Summary of issue'])
    assert result.exit_code == 1
    assert not mock_jira.new_issue.called


@mock.patch('jira_offline.cli.Jira')
def test_cli_new_error_when_passed_epic_ref_for_epic(mock_jira_local, mock_jira):
    '''
    Ensure an error happens when --epic-ref is passed for Epic creation
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    runner = CliRunner()
    result = runner.invoke(cli, ['new', 'TEST', 'Epic', 'Summary of issue', '--epic-ref', 'TEST-1'])
    assert result.exit_code == 1
    assert not mock_jira.new_issue.called


@mock.patch('jira_offline.cli.Jira')
def test_cli_edit_can_change_an_existing_issue(mock_jira_local, mock_jira):
    '''
    Ensure success when editing an existing issue
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    # add fixture to Jira dict
    mock_jira['TEST-71'] = Issue.deserialize(ISSUE_1)

    runner = CliRunner()
    result = runner.invoke(cli, ['edit', 'TEST-71', '--summary', 'A new summary'])
    assert result.exit_code == 0
    assert mock_jira['TEST-71'].summary == 'A new summary'
    assert mock_jira.write_issues.called


@mock.patch('jira_offline.cli.Jira')
def test_cli_edit_can_change_a_new_issue(mock_jira_local, mock_jira):
    '''
    Ensure success when editing a new issue
    '''
    # set function-local instance of Jira class to our test mock
    mock_jira_local.return_value = mock_jira

    # add new issue fixture to Jira dict
    mock_jira['issue_new'] = Issue.deserialize(ISSUE_NEW)

    runner = CliRunner()
    result = runner.invoke(cli, ['edit', 'issue_new', '--summary', 'A new summary'])
    assert result.exit_code == 0
    assert mock_jira['issue_new'].summary == 'A new summary'
    assert mock_jira.write_issues.called
