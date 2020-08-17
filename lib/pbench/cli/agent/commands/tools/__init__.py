import click

from pbench.cli.agent.commands import options
from pbench.cli.agent.commands.tools import clear

#
# subgroup
#
@click.group(help="start/stop/kill/list/register/clear tools")
@options.common_options
@click.pass_context
def tools(ctxt):
    pass


tools.add_command(clear.clear)
