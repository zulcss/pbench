import click

from pbench.cli.agent import options
from pbench.cli.agent.commands.meister import start, stop


@click.group(help="start/stop tool meister")
@options.common_options
@click.pass_context
def meister(ctxt):
    pass


meister.add_command(start.start)
meister.add_command(stop.stop)
