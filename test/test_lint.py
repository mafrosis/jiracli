from unittest import mock

from jira_cli.entrypoint import cli_group_lint_fixversions


def test_lint_fixversions_(mock_jira):
    """
    Ensure CLI lint fixversions command does
    """
    mock_jira.load_issues = mock.Mock()

    mock_params = mock.Mock()

    cli_group_lint_fixversions(mock_params)
