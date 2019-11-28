from unittest import mock

import jira as mod_jira
import pytest

from jira_cli.config import AppConfig
from jira_cli.main import Jira


@pytest.fixture()
def mock_jira():
    """
    Return a basic mock for the core Jira class.

    - Mock the config object with some dummy data
    - Mock the pypi jira module's Jira object. Consuming tests can mock individual methods as
      necessary
    - Mock the _connect method
    - Mock the write_issues method
    """
    jira = Jira()
    jira.config = AppConfig(username='test', password='dummy', projects={'CNTS'})
    jira._connect = mock.Mock()
    jira._jira = mock.Mock(spec=mod_jira.JIRA)
    jira.write_issues = mock.Mock()
    return jira
