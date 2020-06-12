'''
Print and text rendering utils for the CLI commands
'''
import arrow
import click
import pandas as pd
from tabulate import tabulate


def print_list(df: pd.DataFrame, width: int=60, verbose: bool=False, include_project_col: bool=False):
    '''
    Helper to print abbreviated list of issues

    Params:
        df:                   Issues to display in a DataFrame
        width:                Crop width for the summary string
        verbose:              Display more information
        include_project_col:  Include the Issue.project field in a column
    '''
    if df.empty:
        click.echo('No issues in the cache')
        raise click.Abort

    pd.set_option('mode.chained_assignment', None)

    if include_project_col:
        fields = ['project']
    else:
        fields = []

    if not verbose:
        fields += ['issuetype', 'epic_ref', 'summary', 'assignee', 'updated']
    else:
        fields += [
            'issuetype', 'epic_ref', 'epic_name', 'summary', 'assignee', 'fix_versions', 'updated'
        ]
        width = 200

    # replace all NaNs in the DataFrame with blank str
    df.fillna('', inplace=True)

    # pretty dates for non-verbose
    def format_datetime(raw):
        if not raw or pd.isnull(raw):
            return ''
        dt = arrow.get(raw)
        if verbose:
            return f'{dt.format()}'
        else:
            return f'{dt.humanize()}'
    df.updated = df.updated.apply(format_datetime)

    # shorten the summary field for printing
    df.summary = df.summary.str.slice(0, width)

    def abbrev_key(key):
        if key is None:
            return ''
        if len(key) == 36:
            return key[0:8]
        return key
    # abbreviate long issue keys (offline-created issues have a UUID as the key)
    df.key = df.key.apply(abbrev_key)
    df.set_index('key', inplace=True)
    df.epic_ref = df.epic_ref.apply(abbrev_key)

    if verbose:
        df.fix_versions = df.fix_versions.apply(lambda x: '' if not x else ','.join(x))

    print_table(df[fields])


def print_table(df):
    '''Helper to pretty print dataframes'''
    click.echo(tabulate(df, headers='keys', tablefmt='psql'))