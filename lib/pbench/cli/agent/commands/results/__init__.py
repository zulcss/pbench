import click

from pbench.cli.agent import options
from pbench.cli.agent.commands.results import clear


@click.group()
@options.common_options
@click.pass_context
def results(ctxt):
    pass


results.add_command(clear.clear)
