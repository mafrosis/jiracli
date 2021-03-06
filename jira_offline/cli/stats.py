'''
Module containing the stats command group, and all its subcommands
'''
import click

from jira_offline.utils.cli import print_table


@click.group(name='stats', invoke_without_command=True)
@click.option('--project', help='Filter for a specific project')
@click.pass_context
def cli_stats(ctx, project: str=None):
    '''Generate stats on Jira data'''
    # filter issues by project
    ctx.obj.jira.filter.project = project

    # load issues here for all subcommands in the group
    ctx.obj.jira.load_issues()

    if ctx.invoked_subcommand is None:
        for subcommand in (cli_stats_issuetype, cli_stats_status, cli_stats_fix_versions):
            ctx.invoke(subcommand)


@cli_stats.command(name='issuetype')
@click.pass_context
def cli_stats_issuetype(ctx):
    '''Stats on issue type'''
    jira = ctx.obj.jira
    aggregated_issuetype = jira.df.groupby([jira.df.issuetype]).size().to_frame(name='count')
    print_table(aggregated_issuetype)


@cli_stats.command(name='status')
@click.pass_context
def cli_stats_status(ctx):
    '''Stats on ticket status'''
    jira = ctx.obj.jira
    aggregated_status = jira.df.groupby([jira.df.status]).size().to_frame(name='count')
    print_table(aggregated_status)


@cli_stats.command(name='fix-versions')
@click.pass_context
def cli_stats_fix_versions(ctx):
    '''Stats on issue fix-versions'''
    jira = ctx.obj.jira
    jira.df.fix_versions = jira.df.fix_versions.apply(lambda x: ','.join(x) if x else '')
    aggregated_fix_versions = jira.df.groupby([jira.df.fix_versions]).size().to_frame(name='count')
    print_table(aggregated_fix_versions)
