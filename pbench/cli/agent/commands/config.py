import click

from pbench.agent.modules.config import AgentUtilConfig


@click.group()
def config():
    pass


@config.command()
@click.argument("pbench_cfg")
def activate(pbench_cfg):
    command_args = {"config": pbench_cfg}
    AgentUtilConfig(command_args).execute()


#
# backwards agent commands
#
@click.command()
@click.argument("pbench_cfg")
def activate_config(pbench_cfg):
    command_args = {"config": pbench_cfg}
    AgentUtilConfig(command_args).execute()
