import sys

import click

from pbench.agent.utils import setup_logging
from pbench.cli.agent.commands.tools import cli
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class Clear(base.Base, cli.ToolCli):
    """Clear the registered tools"""

    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        try:
            self.clear_tools()
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        except KeyboardInterrupt:
            self.logger.error("Terminating...")
            return 1

        return 0


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
        clictxt.name = []
        if value:
            clictxt.name.append(value)
        return value

    return click.option(
        "-n", "--names", "--name", expose_value=False, callback=callback,
    )(f)


def _remotes_option(f):
    """Pbench noinstall option"""

    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        try:
            clictxt.remotes = value.split(",") if "," in value else [value]
        except Exception:
            clictxt.remotes = []
        return value

    return click.option(
        "-r", "--remotes", "--remote", expose_value=False, callback=callback,
    )(f)


@click.command(help="clear regisered tools")
@options.common_options
@_name_option
@_group_option
@_remotes_option
@context.pass_cli_context
def clear(ctxt):
    status = Clear(ctxt).execute()
    sys.exit(status)
