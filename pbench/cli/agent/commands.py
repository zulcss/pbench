import click

from pbench.agent.modules import config


@click.command()
@click.argument("cfg_file")
def config_activate(cfg_file):
    command_args = {"cfg_file": cfg_file}
    config.PbenchToolConfig(command_args).config_activate()


@click.command()
@click.argument("cfg_file")
@click.argument("keyfile")
def config_ssh_key(cfg_file, keyfile):
    command_args = {"cfg_file": cfg_file, "keyfile": keyfile}
    config.PbenchToolConfig(command_args).config_ssh_key()
