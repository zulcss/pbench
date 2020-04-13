import click

from pbench.agent.modules.cleanup import (
    PbenchCleanup,
    PbenchClearResults,
    PbenchClearTools,
)
from pbench.cli.agent.commands import options


@click.group()
def cleanup():
    pass


@cleanup.command()
def run_dir():
    PbenchCleanup().execute()


@cleanup.command()
def results():
    PbenchClearResults().execute()


@cleanup.command()
@options.tool_clear_options
def tools(group, name):
    command_args = {"group": group, "tool": name}
    PbenchClearTools(command_args).execute()


#
# Backwards compatible commands
#
@click.command()
def pbench_cleanup():
    PbenchCleanup().execute()


@click.command()
def pbench_clear_results():
    PbenchClearResults().execute()


@click.command()
@options.tool_clear_options
def clear_tools(group, name):
    command_args = {"group": group, "tool": name}
    PbenchClearTools(command_args).execute()
