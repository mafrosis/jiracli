from dataclasses import dataclass, field
import logging

import click
import pandas as pd
from tabulate import tabulate

from jira_cli.config import load_config
from jira_cli.main import Jira


logger = logging.getLogger('jira')
sh = logging.StreamHandler()
logger.addHandler(sh)
logger.setLevel(logging.ERROR)


@dataclass
class LintParams:
    fix: bool

@dataclass
class CliParams:
    verbose: bool = field(default=False)
    debug: bool = field(default=False)
    lint: LintParams = field(default=None)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Display INFO level logging')
@click.option('--debug', '-d', is_flag=True, help='Display DEBUG level logging')
@click.pass_context
def cli(ctx, verbose: bool=False, debug: bool=False):
    '''Base CLI options'''
    # setup the logger
    formatter = logging.Formatter('%(levelname)s: %(message)s')

    # handle --verbose and --debug
    if verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    if debug:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f'%(levelname)s: {__name__}:%(lineno)s - %(message)s')

    sh.setFormatter(formatter)
    ctx.obj = CliParams(verbose=verbose, debug=debug)


@cli.command(name='show')
@click.argument('key')
def cli_show(key):
    '''Pretty print an Issue on the CLI'''
    jira = Jira()
    jira.load_issues()
    print(jira[key])


@cli.command(name='pull')
@click.option('--projects', help='Jira project keys')
def cli_pull(projects: list=None):
    '''Fetch and cache all JIRA issues'''
    if projects:
        projects = set(projects.split(','))

    jira = Jira()
    jira.config = load_config(projects)
    jira.pull_issues()

@cli.group(name='stats')
def cli_group_stats():
    'Generate stats on JIRA data'

@cli_group_stats.command(name='issuetype')
def cli_stats_issuetype():
    '''Stats on issue type'''
    jira = Jira()
    df = jira.load_issues()
    aggregated_issuetype = df.groupby([df['issuetype']]).size().to_frame(name='count')
    _print_table(aggregated_issuetype)

@cli_group_stats.command(name='status')
def cli_stats_status():
    '''Stats on ticket status'''
    jira = Jira()
    df = jira.load_issues()
    aggregated_status = df.groupby([df['status']]).size().to_frame(name='count')
    _print_table(aggregated_status)

@cli_group_stats.command(name='fixversions')
def cli_stats_fixversions():
    '''Stats on ticket fixversions'''
    jira = Jira()
    df = jira.load_issues()
    df['fixVersions'] = df['fixVersions'].apply(lambda x: ','.join(x) if x else '')
    aggregated_fixVersions = df.groupby([df['fixVersions']]).size().to_frame(name='count')
    _print_table(aggregated_fixVersions)


@cli.group(name='lint')
@click.option('--fix', is_flag=True, help='Attempt to fix the errors automatically')
@click.pass_context
def cli_group_lint(ctx, fix=False):
    'Report on common mistakes in JIRA issues'
    ctx.obj.lint = LintParams(fix=fix)

@cli_group_lint.command(name='fixversions')
@click.pass_context
def cli_group_lint_fixversions(ctx):
    '''Lint on missing fixVersions field'''
    jira = Jira()
    df = jira.load_issues()

    if ctx.obj.lint.fix:
        # count of all issues missing the fixVersions field
        initial_missing_count = len(df[df.fixVersions.apply(lambda x: len(x) == 0)])

        # set PI5/PI6 on all relevant epics
        for PI in ('PI5', 'PI6'):
            # set PI into fixVersions field on Epics if their name matches
            df[df.epic_name.str.contains(PI)].fixVersions.apply(lambda x: x.add(PI))  # pylint: disable=cell-var-from-loop

            # iterate epics
            for epic_ref in df[df.issuetype == 'Epic'].index:
                # if PI value is set in fixVersions on the epic
                if PI in jira[epic_ref].fixVersions:
                    # filter all issues under this epic, and add PI to fixVersions
                    df[df.epic_ref == jira[epic_ref].key].fixVersions.apply(
                        lambda x: x.add(PI)  # pylint: disable=cell-var-from-loop
                    )

        # Write changes to local cache
        jira.write_issues()

        print('Updated fixVersions on {} issues'.format(
            initial_missing_count - len(df[df.fixVersions.apply(lambda x: len(x) == 0)])
        ))
    else:
        df_missing = df[df['fixVersions'].apply(lambda x: len(x) == 0)]
        print(f'There are {len(df_missing)} issues missing the fixVersions field')
        if ctx.obj.verbose:
            _print_list(df_missing)


@cli.command(name='ls')
def cli_ls():
    '''List Issues on the CLI'''
    jira = Jira()
    jira.load_issues()
    _print_list(jira.df)


def _print_list(df: pd.DataFrame, width=100):
    '''Helper to print abbreviated list of issues'''
    # shorten the summary field for printing
    df['summary'] = df.loc[:]['summary'].str.slice(0, width)
    _print_table(df[['issuetype', 'summary', 'assignee', 'updated']])


def _print_table(df):
    '''Helper to pretty print dataframes'''
    print(tabulate(df, headers='keys', tablefmt='psql'))
