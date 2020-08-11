from pathlib import Path
import socket
import sys

import click

from pbench.agent.utils import setup_logging
from pbench.cli.agent.commands.tools import cli
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class Register(base.Base, cli.ToolCli):
    """Register the registered tools"""

    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        if self.context.labels:
            if not isinstance(self.context.remotes, dict):
                # We already assumed we did this part
                self.context.remotes = {
                    "remotes": self.context.remotes,
                    "labels": self.context.labels,
                }
        else:
            self.context.remotes = {"remotes": self.context.remotes, "labels": None}

        self.register_tool()


def _group_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.group = value
        return value

    return click.option(
        "-g",
        "--groups",
        "--group",
        default="default",
        expose_value=False,
        callback=callback,
    )(f)


def _name_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)

        tool = Path(clictxt.config.pbench_install_dir, "tool-scripts", value)
        if not tool.exists():
            click.secho(f"Could not find {value} in {tool}", fg="red")
            sys.exit(1)

        clictxt.name = value
        return value

    return click.option(
        "-n", "--names", "--name", required=True, expose_value=False, callback=callback,
    )(f)


def _labels_option(f):
    """Pbench labels option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        try:
            clictxt.labels = value.split(",")
        except KeyError:
            clictxt.labels = value.split()
        except Exception:
            clictxt.labels = []
        return value

    return click.option("--labels", expose_value=False, callback=callback,)(f)


def _remotes_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)

        remotes = []
        if value.startswith("@"):
            remote_arg = Path(value.split("@")[1])
            remote = remote_arg.read_text()
            for index, host in enumerate(remote.splitlines()):
                if host and not host.startswith("#"):
                    try:
                        (r, label) = host.split(",")
                        remotes.append({"remote": r, "label": label})
                    except ValueError:
                        remotes.append({"remote": host, "label": None})
                    except Exception:
                        click.secho(
                            f'--remotes=@{remote_arg} contains an invalid file format, expected lines with "<hostname>[,<label>]" at line #${index}',
                            fg="red",
                        )
                        sys.exit(1)
        else:
            try:
                remotes = value.split(",")
            except ValueError:
                remotes = value.split()

        clictxt.remotes = remotes
        return value

    return click.option(
        "-r",
        "--remotes",
        "--remote",
        default=socket.gethostname(),
        expose_value=False,
        callback=callback,
    )(f)


def _noinstall_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
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
        clictxt = ctxt.ensure_object(context.CliContext)
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
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.tool_opts = value
        return value

    return click.argument(
        "tools_opts", nargs=-1, expose_value=False, callback=callback, required=False,
    )(f)


@click.command()
@options.common_options
@_name_option
@_group_option
@_labels_option
@_remotes_option
@_noinstall_option
@_testlabel_option
@_toolopts_option
@context.pass_cli_context
def register(ctxt):
    status = Register(ctxt).execute()
    sys.exit(status)
