from unittest import mock

import jira as mod_jira
import pytest

from jira_cli.config import AppConfig
from jira_cli.main import Jira
from jira_cli.models import ProjectMeta


@pytest.fixture()
def mock_jira_core():
    '''
    Return a Jira class instance with connect method and underlying Jira lib mocked
    '''
    jira = Jira()
    jira.config = AppConfig(username='test', password='dummy', projects={'TEST': ProjectMeta()})
    jira.config.write_to_disk = mock.Mock()
    jira._jira = mock.Mock(spec=mod_jira.JIRA)
    jira.connect = mock.Mock(return_value=jira._jira)
    return jira


@pytest.fixture()
def mock_jira(mock_jira_core):
    '''
    Mock additional methods of Jira class
    '''
    mock_jira_core.load_issues = mock.Mock()
    mock_jira_core.write_issues = mock.Mock()
    mock_jira_core.update_issue = mock.Mock()
    mock_jira_core.new_issue = mock.Mock()
    mock_jira_core.get_project_meta = mock.Mock()
    return mock_jira_core
