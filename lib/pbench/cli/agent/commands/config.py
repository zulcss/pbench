import os
import pwd
import shutil
import sys

import click

from pbench.agent import PbenchAgentConfig
from pbench.agent.utils import setup_logging
from pbench.cli.agent import base, context, options


class Config(base.Base):
    """Copy the configuration file in the right place"""

    def execute(self):
        self.logger = setup_logging(logfile=self.pbench_log)

        pbench_cfg = self.pbench_install_dir / "config"
        try:
            shutil.copy(self.config.pbench_conf, pbench_cfg)
        except shutil.Error as ex:
            self.logger.error(
                "Failed to copy agent configuration file %s", self.config.pbench_conf
            )
            if self.debug:
                self.logger.error(ex)
        except Exception as ex:
            self.logger.error("Unknown exception: %s", ex)

        return 0


class SSH(base.Base):
    """Copy the SSH key in the right place"""

    def execute(self):
        self.logger = setup_logging(logfile=self.pbench_log)

        ssh_key = self.pbench_install_dir / "id_rsa"

        try:
            shutil.copy(self.context.ssh_key, ssh_key)
        except shutil.Error as ex:
            self.logger.error("Failed to copy ssh key %s", ssh_key)
            if self.debug:
                self.logger.error(ex)
        except Exception as ex:
            self.logger.error("Unkwown exception %s", ex)
        finally:
            try:
                uid = pwd.getpwnam(self.config.user).pw_uid
                gid = pwd.getpwnam(self.config.group).pw_gid
            except KeyError:
                self.logger.error(
                    "%s/%s user or group doesnt exist",
                    self.config.user,
                    self.config.group,
                )
            else:
                if ssh_key.exists():
                    os.chown(ssh_key, uid, gid)
                    os.chmod(ssh_key, 0o600)

        return 0


def _config_option(f):
    """Option for agent configuration"""

    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        try:
            if value is None or not os.path.exists(value):
                click.secho(f"Configuration file is not found: {value}", err="Red")
                sys.exit(1)

            clictx.config = PbenchAgentConfig(value)
        except Exception as ex:
            click.secho(f"Failed to load {value}: {ex}", err="red")
            sys.exit(1)

    return click.argument(
        "config", expose_value=False, type=click.Path(exists=True), callback=callback
    )(f)


def _key_file(f):
    """Option for ssh key file"""

    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.ssh_key = value
        return value

    return click.argument(
        "ssh_key", expose_value=False, type=click.Path(exists=True), callback=callback
    )(f)


@click.command(help="copy configuration file")
@options._pbench_agent_debug
@_config_option
@context.pass_cli_context
def activate(ctxt):
    try:
        status = Config(ctxt).execute()
        sys.exit(status)
    except KeyboardInterrupt:
        sys.exit(1)


@click.command(help="copy ssh key")
@options._pbench_agent_debug
@_config_option
@_key_file
@context.pass_cli_context
def ssh(ctxt):
    try:
        status = SSH(ctxt).execute()
        sys.exit(status)
    except KeyboardInterrupt:
        sys.exit(1)


""" Pbench cli sub group"""


@click.group(help="copy ssh key and configuration file")
@options.common_options
@click.pass_context
def config(ctxt):
    pass


config.add_command(activate)
config.add_command(ssh)
