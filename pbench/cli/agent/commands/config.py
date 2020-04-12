import click

from pbench.agent.modules.config import AgentUtilConfig, ConfigSSHKey


@click.group()
def config():
    pass


@config.command()
@click.argument("pbench_cfg")
def activate(pbench_cfg):
    command_args = {"config": pbench_cfg}
    AgentUtilConfig(command_args).execute()


@config.command()
@click.argument("pbench_cfg")
@click.argument("ssh_key")
def ssh(pbench_cfg, ssh_key):
    command_args = {"config": pbench_cfg, "ssh_key": ssh_key}
    ConfigSSHKey(command_args).execute()


#
# backwards agent commands
#
@click.command()
@click.argument("pbench_cfg")
def activate_config(pbench_cfg):
    command_args = {"config": pbench_cfg}
    AgentUtilConfig(command_args).execute()


@click.command()
@click.argument("pbench_cfg")
@click.argument("ssh_key")
def configure_ssh(pbench_cfg, ssh_key):
    command_args = {"config": pbench_cfg, "ssh_key": ssh_key}
    ConfigSSHKey(command_args).execute()
