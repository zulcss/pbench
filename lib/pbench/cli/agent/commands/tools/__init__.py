import click

from pbench.cli.agent import options
from pbench.cli.agent.commands.tools import process

#
# subgroup
#
@click.group(help="start/stop/kill/list/register/clear tools")
@options.common_options
@click.pass_context
def tools(ctxt):
    pass


tools.add_command(process.postprocess)
tools.add_command(process.start)
tools.add_command(process.stop)
tools.add_command(process.kill)
