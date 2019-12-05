from jira_cli.main import Jira

from jira_cli.linters import fixversions as lint_fixversions


def fixversions():
    df = Jira.load_issues()
    print('There are {} issues missing the fixVersions field'.format(
        len(df[df['fixVersions'].apply(lambda x: len(x) == 0)])
    ))
