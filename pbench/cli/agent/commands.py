import click

from pbench.agent.modules import cleanup
from pbench.agent.modules import config
from pbench.cli.agent import options

@click.command()
@click.option('-g', '--group',
                    default='default',
                    help="the group from which tools should be removed \n"
                         "(the default group is 'default')")
@click.option('-n', '--name',
              help="a specific tool to be removed. If no tool is removed "
                    "all tools in the group are removed")
def clear_tools(group, name):
    command_args = {'group': group, 'name': name}
    cleanup.PbenchCleanup(command_args).clear_tools()

@click.command()
def pbench_cleanup():
    cleanup.PbenchCleanup().cleanup()

@click.command()
def clear_results():
    cleanup.PbenchCleanup().clear_results()

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
