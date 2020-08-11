import click

from pbench.cli.agent import options
from pbench.cli.agent.commands.triggers import list
from pbench.cli.agent.commands.triggers import register


@click.group()
@options.common_options
@click.pass_context
def triggers(ctxt):
    pass


triggers.add_command(list.list)
triggers.add_command(register.register)
