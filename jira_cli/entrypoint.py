'''
Application CLI entrypoint. Uses the click library to configure commands and subcommands, arguments,
options and help text.
'''
from dataclasses import dataclass, field
import logging
from typing import Optional, Set

import click
import arrow
import pandas as pd
from tabulate import tabulate

from jira_cli.config import get_user_creds
from jira_cli.create import create_issue
from jira_cli.exceptions import FailedPullingProjectMeta, JiraApiError, ProjectNotConfigured
from jira_cli.linters import fixversions as lint_fixversions
from jira_cli.linters import issues_missing_epic as lint_issues_missing_epic
from jira_cli.main import Jira
from jira_cli.sync import pull_issues, push_issues


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
    lint: Optional[LintParams] = field(default=None)

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

    if key not in jira:
        click.echo('Unknown issue key')
        raise click.Abort

    click.echo(jira[key])


@cli.command(name='push')
@click.pass_context
def cli_push(ctx):
    '''Synchronise changes back to Jira server'''
    jira = Jira()
    jira.load_issues()

    if not jira:
        click.echo('No issues in the cache')
        raise click.Abort

    push_issues(jira, verbose=ctx.obj.verbose)


@cli.command(name='clone')
@click.argument('project')
@click.option('--username', help='Basic auth username to authenicate with')
@click.pass_context
def cli_clone(ctx, project: str, username: str=None):
    '''
    Clone a Jira project to offline

    PROJECT - Jira project key to configure and pull
    '''
    if ',' in project:
        click.echo('You should pass only a single project key')
        raise click.Abort

    jira = Jira()

    # always ask for credentials when cloning
    get_user_creds(jira.config, username)

    try:
        # retrieve project metadata
        jira.config.projects[project] = jira.get_project_meta(project)
        jira.config.write_to_disk()
    except JiraApiError as e:
        raise FailedPullingProjectMeta(e)

    # and finally pull all the project's issues
    pull_issues(jira, projects={project}, verbose=ctx.obj.verbose)


@cli.command(name='pull')
@click.option('--projects', help='Jira project keys')
@click.option('--username', help='Basic auth username to authenicate with')
@click.option('--login', is_flag=True, help='Reset the current login credentials')
@click.option('--reset-hard', is_flag=True, help='Force reload of all issues. This will destroy any local changes!')
@click.pass_context
def cli_pull(ctx, projects: str=None, username: str=None, login: bool=False, reset_hard: bool=False):
    '''Fetch and cache all Jira issues'''
    projects_set: Optional[Set[str]] = None
    if projects:
        projects_set = set(projects.split(','))

    jira = Jira()
    if login or username:
        # refresh Jira credentials
        get_user_creds(jira.config, username)

    if reset_hard:
        reset_warning = None
        if projects:
            reset_warning = f'{projects}'
        else:
            reset_warning = f'{jira.config.projects}'

        if reset_warning:
            click.confirm(
                f'Warning! This will destroy any local changes for project(s) {reset_warning}. Continue?',
                abort=True
            )

    pull_issues(jira, projects=projects_set, force=reset_hard, verbose=ctx.obj.verbose)


@cli.command(name='new')
@click.argument('project')
@click.argument('issuetype')
@click.argument('summary')
@click.option('--assignee', help='Username of person assigned to complete the Issue')
@click.option('--description', help='Long description of Issue')
@click.option('--epic-name', help='Short epic name')
@click.option('--epic-ref', help='Epic key to which this Issue belongs')
@click.option('--estimate', help='Issue size estimate in story points', type=int)
@click.option('--fix-versions', help='Issue fix versions as comma-separated')
@click.option('--labels', help='Issue labels as comma-separated')
@click.option('--reporter', help='Username of Issue reporter (defaults to creator)')
def cli_new(project: str, issuetype: str, summary: str, **kwargs):
    '''
    Create a new issue on a project

    PROJECT    Jira project key for the new issue
    ISSUETYPE  A valid issue type for the specified project
    SUMMARY    Mandatory free text oneliner for this issue
    '''
    jira = Jira()

    if ',' in project:
        click.echo('You should pass only a single project key')
        raise click.Abort

    if jira.config and project not in jira.config.projects:
        raise ProjectNotConfigured(project)

    # validate epic parameters
    if issuetype == 'Epic':
        if kwargs.get('epic_ref'):
            click.echo('You cannot pass --epic-ref when creating an Epic!')
            raise click.Abort
        if not kwargs.get('epic_name'):
            click.echo('You must pass --epic-name when creating an Epic!')
            raise click.Abort
    else:
        if kwargs.get('epic_name'):
            click.echo('Parameter --epic-name is ignored for anything other than an Epic')

    # parse fixVersions and labels
    if kwargs.get('fix_versions'):
        # note key change of --fix_versions -> Issue.fixVersions
        kwargs['fixVersions'] = set(kwargs['fix_versions'].split(','))
        del kwargs['fix_versions']
    if kwargs.get('labels'):
        kwargs['labels'] = set(kwargs['labels'].split(','))

    # create an Issue offline, it is sync'd on push
    new_issue = create_issue(jira, project, issuetype, summary, **kwargs)

    # display the new issue
    click.echo(new_issue)


@cli.group(name='stats', invoke_without_command=True)
@click.pass_context
def cli_group_stats(ctx):
    '''Generate stats on Jira data'''
    ctx.obj.jira = Jira()
    ctx.obj.jira.load_issues()

    if ctx.invoked_subcommand is None:
        for subcommand in (cli_stats_issuetype, cli_stats_status, cli_stats_fixversions):
            ctx.invoke(subcommand)

@cli_group_stats.command(name='issuetype')
@click.pass_context
def cli_stats_issuetype(ctx):
    '''Stats on issue type'''
    jira = ctx.obj.jira
    aggregated_issuetype = jira.df.groupby([jira.df.issuetype]).size().to_frame(name='count')
    _print_table(aggregated_issuetype)

@cli_group_stats.command(name='status')
@click.pass_context
def cli_stats_status(ctx):
    '''Stats on ticket status'''
    jira = ctx.obj.jira
    aggregated_status = jira.df.groupby([jira.df.status]).size().to_frame(name='count')
    _print_table(aggregated_status)

@cli_group_stats.command(name='fixversions')
@click.pass_context
def cli_stats_fixversions(ctx):
    '''Stats on ticket fixversions'''
    jira = ctx.obj.jira
    jira.df.fixVersions = jira.df.fixVersions.apply(lambda x: ','.join(x) if x else '')
    aggregated_fixVersions = jira.df.groupby([jira.df.fixVersions]).size().to_frame(name='count')
    _print_table(aggregated_fixVersions)


@cli.group(name='lint')
@click.option('--fix', is_flag=True, help='Attempt to fix the errors automatically')
@click.pass_context
def cli_group_lint(ctx, fix=False):
    'Report on common mistakes in Jira issues'
    ctx.obj.lint = LintParams(fix=fix)

@cli_group_lint.command(name='fixversions')
@click.option('--value', help='Value set in fixVersions. Used with --fix.')
@click.pass_context
def cli_group_lint_fixversions(ctx, value=None):
    '''
    Lint on missing fixVersions field
    '''
    if ctx.obj.lint.fix and not value:
        raise click.BadParameter('You must pass --value with --fix', ctx)

    if value:
        if not ctx.obj.lint.fix:
            logger.warning('Passing --value without --fix has no effect')

    jira = Jira()
    jira.load_issues()

    # query issues missing the fixVersions field
    df = lint_fixversions(jira, fix=False)
    initial_missing_count = len(df)

    if ctx.obj.lint.fix:
        df = lint_fixversions(jira, fix=ctx.obj.lint.fix, value=value)

        click.echo(f'Updated fixVersions on {initial_missing_count - len(df)} issues')
    else:
        click.echo(f'There are {len(df)} issues missing the fixVersions field')

    if ctx.obj.verbose:
        _print_list(df, verbose=ctx.obj.verbose)

@cli_group_lint.command(name='issues-missing-epic')
@click.option('--epic-ref', help='Epic to set on issues with no epic. Used with --fix.')
@click.pass_context
def cli_group_lint_issues_missing_epic(ctx, epic_ref=None):
    '''
    Lint issues without an epic set
    '''
    if ctx.obj.lint.fix and not epic_ref:
        raise click.BadParameter('You must pass --epic_ref with --fix', ctx)

    if epic_ref:
        if not ctx.obj.lint.fix:
            logger.warning('Passing --epic-ref without --fix has no effect')

    jira = Jira()
    jira.load_issues()

    # query issues missing the epic field
    df = lint_issues_missing_epic(jira, fix=False)
    initial_missing_count = len(df)

    if ctx.obj.lint.fix:
        df = lint_issues_missing_epic(jira, fix=ctx.obj.lint.fix, epic_ref=epic_ref)

        click.echo(f'Set epic to {epic_ref} on {initial_missing_count - len(df)} issues')
    else:
        click.echo(f'There are {len(df)} issues missing an epic')

    if ctx.obj.verbose:
        _print_list(df, verbose=ctx.obj.verbose)


@cli.command(name='ls')
@click.pass_context
def cli_ls(ctx):
    '''List Issues on the CLI'''
    jira = Jira()
    jira.load_issues()
    _print_list(jira.df, verbose=ctx.obj.verbose)


def _print_list(df: pd.DataFrame, width: int=60, verbose: bool=False):
    '''
    Helper to print abbreviated list of issues

    Params:
        df:       Issues to display in a DataFrame
        width:    Crop width for the summary string
        verbose:  Display more information
    '''
    if df.empty:
        click.echo('No issues in the cache')
        raise click.Abort

    if not verbose:
        fields = ['issuetype', 'epic_ref', 'summary', 'assignee', 'updated']
    else:
        fields = ['issuetype', 'epic_ref', 'epic_name', 'summary', 'assignee', 'fixVersions',
                  'updated']
        width = 200

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
    df.summary = df.loc[:]['summary'].str.slice(0, width)

    # abbreviate UUID issue keys (these are on offline-created Issues)
    def abbrev_key(key):
        if key is None:
            return ''
        if len(key) == 36:
            return key[0:8]
        return key
    df.set_index(df.key.apply(abbrev_key), inplace=True)
    df.epic_ref = df.epic_ref.apply(abbrev_key)

    if verbose:
        df.fixVersions = df.fixVersions.apply(lambda x: '' if not x else ','.join(x))

    _print_table(df[fields])


def _print_table(df):
    '''Helper to pretty print dataframes'''
    click.echo(tabulate(df, headers='keys', tablefmt='psql'))
