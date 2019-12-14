from dataclasses import dataclass, field
import logging

import click
import pandas as pd
from tabulate import tabulate

from jira_cli.config import load_config
from jira_cli.linters import fixversions as lint_fixversions
from jira_cli.linters import issues_missing_epic as lint_issues_missing_epic
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
@click.pass_context
def cli_pull(ctx, projects: list=None):
    '''Fetch and cache all JIRA issues'''
    if projects:
        projects = set(projects.split(','))

    jira = Jira()
    jira.config = load_config(projects)
    jira.pull_issues(verbose=ctx.obj.verbose)

@cli.group(name='stats')
def cli_group_stats():
    'Generate stats on JIRA data'

@cli_group_stats.command(name='issuetype')
def cli_stats_issuetype():
    '''Stats on issue type'''
    jira = Jira()
    jira.load_issues()
    aggregated_issuetype = jira.df.groupby([jira.df.issuetype]).size().to_frame(name='count')
    _print_table(aggregated_issuetype)

@cli_group_stats.command(name='status')
def cli_stats_status():
    '''Stats on ticket status'''
    jira = Jira()
    jira.load_issues()
    aggregated_status = jira.df.groupby([jira.df.status]).size().to_frame(name='count')
    _print_table(aggregated_status)

@cli_group_stats.command(name='fixversions')
def cli_stats_fixversions():
    '''Stats on ticket fixversions'''
    jira = Jira()
    jira.load_issues()
    jira.df.fixVersions = jira.df.fixVersions.apply(lambda x: ','.join(x) if x else '')
    aggregated_fixVersions = jira.df.groupby([jira.df.fixVersions]).size().to_frame(name='count')
    _print_table(aggregated_fixVersions)


@cli.group(name='lint')
@click.option('--fix', is_flag=True, help='Attempt to fix the errors automatically')
@click.pass_context
def cli_group_lint(ctx, fix=False):
    'Report on common mistakes in JIRA issues'
    ctx.obj.lint = LintParams(fix=fix)

@cli_group_lint.command(name='fixversions')
@click.option('--words', help='Words to look for in an Epic name, and set in fixVersions. Used with --fix.')
@click.pass_context
def cli_group_lint_fixversions(ctx, words=None):
    '''
    Lint on missing fixVersions field
    '''
    if ctx.obj.lint.fix and not words:
        raise click.BadParameter('You must pass --words with --fix', ctx)

    if words:
        if not ctx.obj.lint.fix:
            logger.warning('Passing --words without --fix has no effect')
        words = set(words.split(','))

    # query issues missing the fixVersions field
    df = lint_fixversions(fix=False)
    initial_missing_count = len(df)

    if ctx.obj.lint.fix:
        df = lint_fixversions(ctx.obj.lint.fix, words)

        print(f'Updated fixVersions on {initial_missing_count - len(df)} issues')
    else:
        print(f'There are {len(df)} issues missing the fixVersions field')

    if ctx.obj.verbose:
        _print_list(df)

@cli_group_lint.command(name='issues-without-epic')
@click.option('--epic-ref', help='Epic to set on issues with no epic. Used with --fix.')
@click.pass_context
def cli_group_lint_issues_missing_epic(ctx, epic_ref=None):
    '''
    Lint issues without an epic set
    '''
    if epic_ref:
        if not ctx.obj.lint.fix:
            logger.warning('Passing --epic-ref without --fix has no effect')

    # query issues missing the epic field
    df = lint_issues_missing_epic(fix=False)
    initial_missing_count = len(df)

    if ctx.obj.lint.fix:
        df = lint_issues_missing_epic(ctx.obj.lint.fix, epic_ref)

        print(f'Set epic to {epic_ref} on {initial_missing_count - len(df)} issues')
    else:
        print(f'There are {len(df)} issues missing an epic')

    if ctx.obj.verbose:
        _print_list(df)


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
