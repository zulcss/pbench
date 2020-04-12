import click

from pbench.cli.agent.commands import config
from pbench.cli.agent.commands import cleanup


@click.group()
def main():
    pass


main.add_command(config.config)
main.add_command(cleanup.cleanup)
