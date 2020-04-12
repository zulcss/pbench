import click

from pbench.cli.agent.commands import config


@click.group()
def main():
    pass


main.add_command(config.config)
