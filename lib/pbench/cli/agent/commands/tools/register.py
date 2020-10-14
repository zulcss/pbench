"""
"""
import socket
import sys
import os
import pathlib

import click

from pbench.agent.utils import setup_logging
from pbench.cli.agent import CliContext, pass_cli_context
from pbench.cli.agent.commands.tools.base import ToolCommand
from pbench.cli.agent.options import common_options


class RegisterTool(ToolCommand):
    def __init__(self, context):
        super().__init__(context)

        self.logger = setup_logging(logfile=self.pbench_log)

    def execute(self):
        tool_file = self.pbench_install_dir / "tool-scripts" / self.context.name
        if not tool_file.exists():
            self.logger.error(
                "Could not find %s in %s/tool-scripts/: has this tool been integrated into the pbench-agent?",
                self.context.name,
                self.pbench_install_dir,
            )
            return 1

        if self.context.remotes_arg.startswith("@"):
            if self.context.labels_arg:
                self.logger.error(
                    "--labels=%s not allowed with remotes file (%s)",
                    self.context.labels_arg,
                    self.context.remotes_arg,
                )
                return 1
            remotes_file = pathlib.Path(self.context.remotes_arg)
            if remotes_file.exists():
                self.logger.error(
                    "--remotes=@%s specifies a file that does not exist", remotes_file
                )
                return 1

            remotes = [remote for remote in remotes_file.read_text().splitlines()]
            remote = dict()

            for index, hosts in enumerate(remotes):
                if hosts and not hosts.startswith("#"):
                    count = hosts.count(",")
                    if count == 0:
                        remote.update({hosts: None})
                    elif count == 1:
                        host, label = hosts.split(",")
                        remote.update({host: label})
                    elif count == 2:
                        self.logger.error(
                            '--remotes=@%s contains an invalid file format, expected lines with "<hostname>[,<label>]" at line #%s',
                            remotes_file,
                            index,
                        )
        else:
            try:
                remotes = self.context.remotes_arg.split(",")
            except Exception:
                self.logger.error(
                    "INTERNAL: missing -r|--remote|--remotes=<remote-host>[,<remote-host>] argument for some unknown reason (should not happen)"
                )
                return 1

            if self.context.labels_arg:
                labels = self.context.labels_arg.split(",")
                if len(remote) == len(labels):
                    # We emit an error message now if we
                    # are not working on behalf of
                    # pbench-register-tool-set, since it
                    # will handle its own error message on
                    # failure.
                    self.logger.error(
                        'The number of labels given, "%s", does not match the number of remotes given, "%s"',
                        self.context.labels_arg,
                        self.context.remotes_arg,
                    )
                    return 1

                # Now create an dict for labels, where the index is
                # by given hostname from the remotes.
                remote = dict(zip(self.context.remotes_arg, self.context.labels_arg))
            else:
                remote = {
                    remote: None for remote in self.context.remotes_arg.split(",")
                }

        if self.context.testlabel:
            # Used by pbench-register-tool-set to avoid duplicating logic, we
            # have been asked to exit early successfully if all argument
            # processing has been successful so far.
            return 0

        tool_opts = []
        print(self.context.toolopts)
        """
        tg_dir = self.gen_tools_group_dir(self.context.group)
        tg_dir.mkdir(parents=True, exist_ok=True)
        if not tg_dir.exists():
            self.logger.error(
                "Unable to creat the necessary tools group directory, %s",
                tg_dir)
            return 1
        """
        return 0


def _group_option(f):
    """Group name option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.group = value
        return value

    return click.option(
        "-g",
        "--group",
        default="default",
        expose_value=False,
        callback=callback,
        help="list the tools used in this <group-name>",
    )(f)


def _name_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.name = value
        return value

    return click.option(
        "-n", "--names", "--name", required=True, expose_value=False, callback=callback,
    )(f)


def _labels_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.labels_arg = value
        return value

    return click.option("--labels", expose_value=False, callback=callback,)(f)


def _remotes_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.remotes_arg = value
        return value

    if os.environ.get("_PBENCH_UNIT_TESTS"):
        hostname = "testhost.example.com"
    else:
        hostname = socket.gethostname()

    return click.option(
        "-r",
        "--remotes",
        "--remote",
        default=hostname,
        expose_value=False,
        callback=callback,
    )(f)


def _noinstall_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.noinstall = value
        return value

    return click.option(
        "--no-install",
        expose_value=False,
        is_flag=True,
        default=False,
        callback=callback,
    )(f)


def _testlabel_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.testlabel = value
        return value

    return click.option(
        "--test-labels",
        expose_value=False,
        is_flag=True,
        default=False,
        callback=callback,
    )(f)


def _toolopts_option(f):
    """Pbench toolopts option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(CliContext)
        clictxt.tool_opts = value
        return value

    return click.argument(
        "tools_opts", nargs=-1, expose_value=False, callback=callback, required=False
    )(f)


@click.command(help="clear all tools or filter by name or group")
@common_options
@_name_option
@_group_option
@_labels_option
@_remotes_option
@_noinstall_option
@_testlabel_option
@_toolopts_option
@pass_cli_context
def main(ctxt):
    status = RegisterTool(ctxt).execute()
    sys.exit(status)
